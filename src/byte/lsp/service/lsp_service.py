from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from lsp_client import Client, Position, PyreflyClient
from lsp_client.clients.basedpyright import BasedpyrightClient
from lsp_client.clients.deno import DenoClient
from lsp_client.clients.gopls import GoplsClient
from lsp_client.clients.pyright import PyrightClient
from lsp_client.clients.rust_analyzer import RustAnalyzerClient
from lsp_client.clients.ty import TyClient
from lsp_client.clients.typescript import TypescriptClient
from lsp_client.server import ContainerServer, LocalServer

from byte import Service, TaskManager
from byte.lsp import (
    CompletionItem,
    ContainerServerConfig,
    CustomServerConfig,
    HoverResult,
    LocalServerConfig,
    Location,
    Position as BytePosition,
    PresetServerConfig,
    Range,
)
from byte.support.utils import get_language_from_filename

# Mapping of preset names to their client classes
PRESET_CLIENTS: Dict[str, Type[Client]] = {
    "pyright": PyrightClient,
    "basedpyright": BasedpyrightClient,
    "pyrefly": PyreflyClient,
    "ty": TyClient,
    "rust_analyzer": RustAnalyzerClient,
    "deno": DenoClient,
    "typescript": TypescriptClient,
    "gopls": GoplsClient,
}

# Mapping of preset names to their supported languages
PRESET_LANGUAGES: Dict[str, List[str]] = {
    "pyright": ["python"],
    "basedpyright": ["python"],
    "pyrefly": ["python"],
    "ty": ["python"],
    "rust_analyzer": ["rust"],
    "deno": ["typescript", "javascript"],
    "typescript": ["typescript", "javascript"],
    "gopls": ["go"],
}


class LSPService(Service):
    """Service for managing multiple LSP servers and providing code intelligence.

    Manages LSP client lifecycle, routes requests to appropriate servers based on
    file languages, and provides a unified interface for code intelligence features.
    Usage: `hover = await lsp_service.get_hover(file_path, line, char)` -> hover info
    """

    async def _create_server_from_config(
        self, server_config: LocalServerConfig | ContainerServerConfig
    ) -> LocalServer | ContainerServer:
        """Create a server instance from configuration."""
        if server_config.type == "local":
            return LocalServer(program=server_config.program, args=server_config.args)
        else:
            return ContainerServer(
                image=server_config.image,
                workspace=self.app["path"],
                workspace_mount=server_config.workspace_mount,
            )

    async def _create_preset_client(self, server_name: str, config: PresetServerConfig) -> Client:
        """Create a preset client from configuration."""
        client_class = PRESET_CLIENTS[config.preset]

        # Get the default servers from the client class
        temp_client = client_class()
        default_servers = temp_client.create_default_servers()

        # Select server based on server_type preference
        if config.server_type == "local" and default_servers.local:
            server = default_servers.local
        elif config.server_type == "container" and default_servers.container:
            server = default_servers.container
        elif default_servers.container:
            # Fallback to container if preferred type not available
            server = default_servers.container
        elif default_servers.local:
            # Fallback to local if container not available
            server = default_servers.local
        else:
            raise ValueError(f"No server available for preset '{config.preset}'")

        # Create client with selected server and workspace
        client = client_class(server=server, workspace=self.app["path"])

        # Override initialization options if provided
        if config.initialization_options:
            # Store custom init options to override in client
            client._custom_init_options = config.initialization_options

        return client

    async def _create_custom_client(self, server_name: str, config: CustomServerConfig) -> Client:
        """Create a custom client from configuration."""
        # Create server from config
        server = await self._create_server_from_config(config.server)

        # Create a dynamic client class for this custom server
        class CustomClient(Client):
            def create_default_servers(self):
                from lsp_client.server import DefaultServers

                return DefaultServers(
                    local=server if isinstance(server, LocalServer) else None,
                    container=server if isinstance(server, ContainerServer) else None,
                )

            def create_initialization_options(self) -> dict:
                return config.initialization_options or {}

        # Instantiate the custom client
        return CustomClient(server=server, workspace=self.app["path"])

    async def _start_lsp_client(self, server_name: str) -> None:
        """Start a single LSP client in background."""
        try:
            server_config = self.app["config"].lsp.servers[server_name]

            self.app["log"].info(f"Starting LSP server: {server_name}")

            # Create client based on config type
            if isinstance(server_config, PresetServerConfig):
                client = await self._create_preset_client(server_name, server_config)
            else:
                client = await self._create_custom_client(server_name, server_config)

            # Start the client (enters async context)
            await client.__aenter__()

            self.clients[server_name] = client
            self.app["log"].info(f"LSP server started successfully: {server_name}")

        except Exception as e:
            self.app["log"].error(f"Error starting LSP server {server_name}: {e}")
            self.app["log"].exception(e)

    async def _start_lsp_servers(self) -> None:
        """Start all configured LSP servers in background."""
        for server_name in self.app["config"].lsp.servers.keys():
            self.task_manager.start_task(f"lsp_server_{server_name}", self._start_lsp_client(server_name))

    def boot(self) -> None:
        """Initialize LSP service with configured servers."""
        self.clients: Dict[str, Client] = {}
        self.language_map: Dict[str, str] = {}
        self.task_manager = self.app.make(TaskManager)

        # Build language to server name mapping
        for server_name, server_config in self.app["config"].lsp.servers.items():
            if isinstance(server_config, PresetServerConfig):
                # Use preset language mapping
                languages = PRESET_LANGUAGES.get(server_config.preset, [])
            else:
                # Use custom config languages
                languages = server_config.languages

            for language in languages:
                # Store languages in lowercase for case-insensitive matching
                self.language_map[language.lower()] = server_name

        # Start LSP servers in background if enabled
        if self.app["config"].lsp.enable:
            self.task_manager.start_task("lsp_servers_init", self._start_lsp_servers())

    async def _get_client_for_file(self, file_path: Path) -> Optional[Client]:
        """Get an LSP client for the given file.

        Usage: Internal method to route file to appropriate LSP server
        """
        if not self.app["config"].lsp.enable:
            return None

        # Get the language for this file using Pygments
        file_language = get_language_from_filename(str(file_path))

        if not file_language:
            self.app["log"].debug(f"Could not determine language for file: {file_path}")
            return None

        # Determine server from file language (case-insensitive)
        server_name = self.language_map.get(file_language.lower())

        if not server_name or server_name not in self.app["config"].lsp.servers:
            self.app["log"].debug(f"No LSP server configured for language '{file_language}' (file: {file_path})")
            return None

        # Return existing client if available
        client = self.clients.get(server_name)
        if client:
            return client

        # If client not ready yet, log a warning
        self.app["log"].warning(f"LSP client '{server_name}' not ready yet for file: {file_path}")
        return None

    async def handle(self, **kwargs) -> Any:
        """Handle LSP service operations.

        Usage: `await lsp_service.handle(operation="hover", file_path=path, line=10, character=5)`
        """
        operation = kwargs.get("operation")
        file_path = kwargs.get("file_path")

        if not operation or not file_path:
            return None

        line = kwargs.get("line", 0)
        character = kwargs.get("character", 0)

        if operation == "hover":
            return await self.get_hover(file_path, line, character)
        elif operation == "references":
            return await self.find_references(file_path, line, character)
        elif operation == "definition":
            return await self.goto_definition(file_path, line, character)
        elif operation == "declaration":
            return await self.goto_declaration(file_path, line, character)
        elif operation == "type_definition":
            return await self.goto_type_definition(file_path, line, character)
        elif operation == "completions":
            return await self.get_completions(file_path, line, character)
        elif operation == "signature_help":
            return await self.get_signature_help(file_path, line, character)

        return None

    async def get_hover(self, file_path: Path, line: int, character: int) -> Optional[HoverResult]:
        """Get hover information for any supported file.

        Usage: `await lsp_service.get_hover(Path("src/main.ts"), 10, 5)` -> hover info
        """
        client = await self._get_client_for_file(file_path)
        if not client:
            return None

        if line < 0 or character < 0:
            return None

        try:
            result = await client.request_hover(file_path=str(file_path), position=Position(line, character))  # ty:ignore[unresolved-attribute]
        except ValueError:
            return None

        if result and hasattr(result, "value"):
            # Convert lsp-client result to our HoverResult
            return HoverResult(contents=str(result.value))

        return None

    async def find_references(self, file_path: Path, line: int, character: int) -> List[Location]:
        """Find references for any supported file.

        Usage: `await lsp_service.find_references(Path("src/main.ts"), 10, 5)` -> list of locations
        """
        client = await self._get_client_for_file(file_path)
        if not client:
            return []

        try:
            results = await client.request_references(file_path=str(file_path), position=Position(line, character))  # ty:ignore[unresolved-attribute]
        except ValueError:
            return []

        if results is None:
            return []

        # Convert lsp-client results to our Location objects
        locations = []
        for result in results:
            locations.append(
                Location(
                    uri=str(result.uri),
                    range=Range(
                        start=BytePosition(line=result.range.start.line, character=result.range.start.character),
                        end=BytePosition(line=result.range.end.line, character=result.range.end.character),
                    ),
                )
            )

        return locations

    async def goto_definition(self, file_path: Path, line: int, character: int) -> List[Location]:
        """Go to definition for any supported file.

        Usage: `await lsp_service.goto_definition(Path("src/main.ts"), 10, 5)` -> definition locations
        """
        client = await self._get_client_for_file(file_path)
        if not client:
            return []
        try:
            results = await client.request_definition(file_path=str(file_path), position=Position(line, character))  # ty:ignore[unresolved-attribute]
        except ValueError:
            return []

        if results is None:
            return []

        # Convert lsp-client results to our Location objects
        locations = []
        for result in results:
            locations.append(
                Location(
                    uri=str(result.target_uri),
                    range=Range(
                        start=BytePosition(
                            line=result.target_selection_range.start.line,
                            character=result.target_selection_range.start.character,
                        ),
                        end=BytePosition(
                            line=result.target_selection_range.end.line,
                            character=result.target_selection_range.end.character,
                        ),
                    ),
                )
            )

        return locations

    async def get_completions(self, file_path: Path, line: int, character: int) -> List[CompletionItem]:
        """Get completions for any supported file.

        Usage: `await lsp_service.get_completions(Path("src/main.ts"), 10, 5)` -> completion items
        """
        client = await self._get_client_for_file(file_path)
        if not client:
            return []

        try:
            results = await client.request_completion(file_path=str(file_path), position=Position(line, character))  # ty:ignore[unresolved-attribute]
        except ValueError:
            return []

        # Convert lsp-client results to our CompletionItem objects
        items = []
        for result in results:
            # Extract documentation value from MarkupContent if present
            documentation = None
            if hasattr(result, "documentation") and result.documentation:
                if hasattr(result.documentation, "value"):
                    documentation = result.documentation.value
                else:
                    documentation = str(result.documentation)

            items.append(
                CompletionItem(
                    label=result.label,
                    kind=result.kind if hasattr(result, "kind") else None,
                    detail=result.detail if hasattr(result, "detail") else None,
                    documentation=documentation,
                )
            )

        return items

    async def goto_declaration(self, file_path: Path, line: int, character: int) -> List[Location]:
        """Go to declaration for any supported file.

        Usage: `await lsp_service.goto_declaration(Path("src/main.ts"), 10, 5)` -> declaration locations
        """
        client = await self._get_client_for_file(file_path)
        if not client:
            return []

        try:
            results = await client.request_declaration(file_path=str(file_path), position=Position(line, character))  # ty:ignore[unresolved-attribute]
        except ValueError:
            return []

        # Convert lsp-client results to our Location objects
        locations = []
        for result in results:
            locations.append(
                Location(
                    uri=str(result.target_uri),
                    range=Range(
                        start=BytePosition(
                            line=result.target_selection_range.start.line,
                            character=result.target_selection_range.start.character,
                        ),
                        end=BytePosition(
                            line=result.target_selection_range.end.line,
                            character=result.target_selection_range.end.character,
                        ),
                    ),
                )
            )

        return locations

    async def goto_type_definition(self, file_path: Path, line: int, character: int) -> List[Location]:
        """Go to type definition for any supported file.

        Usage: `await lsp_service.goto_type_definition(Path("src/main.ts"), 10, 5)` -> type definition locations
        """
        client = await self._get_client_for_file(file_path)
        if not client:
            return []

        try:
            results = await client.request_type_definition(file_path=str(file_path), position=Position(line, character))  # ty:ignore[unresolved-attribute]
        except ValueError:
            return []

        # Convert lsp-client results to our Location objects
        locations = []
        for result in results:
            locations.append(
                Location(
                    uri=str(result.target_uri),
                    range=Range(
                        start=BytePosition(
                            line=result.target_selection_range.start.line,
                            character=result.target_selection_range.start.character,
                        ),
                        end=BytePosition(
                            line=result.target_selection_range.end.line,
                            character=result.target_selection_range.end.character,
                        ),
                    ),
                )
            )

        return locations

    async def get_signature_help(self, file_path: Path, line: int, character: int) -> Optional[Dict[str, Any]]:
        """Get signature help for any supported file.

        Usage: `await lsp_service.get_signature_help(Path("src/main.ts"), 10, 5)` -> signature help info
        """
        client = await self._get_client_for_file(file_path)
        if not client:
            return None

        try:
            result = await client.request_signature_help(file_path=str(file_path), position=Position(line, character))  # ty:ignore[unresolved-attribute]
        except ValueError:
            return None

        if result:
            # Convert SignatureHelp to dict format
            signatures = []
            if hasattr(result, "signatures"):
                for sig in result.signatures:
                    sig_dict = {"label": sig.label}

                    if hasattr(sig, "documentation") and sig.documentation:
                        sig_dict["documentation"] = str(sig.documentation)

                    if hasattr(sig, "parameters") and sig.parameters:
                        params = []
                        for param in sig.parameters:
                            param_dict = {}
                            if hasattr(param, "label"):
                                param_dict["label"] = param.label
                            if hasattr(param, "documentation") and param.documentation:
                                param_dict["documentation"] = str(param.documentation)
                            params.append(param_dict)
                        sig_dict["parameters"] = params

                    if hasattr(sig, "active_parameter"):
                        sig_dict["active_parameter"] = sig.active_parameter

                    signatures.append(sig_dict)

            return {
                "signatures": signatures,
                "active_signature": result.active_signature if hasattr(result, "active_signature") else 0,
                "active_parameter": result.active_parameter if hasattr(result, "active_parameter") else 0,
            }

        return None

    async def shutdown_all(self) -> None:
        """Shutdown all running LSP servers.

        Usage: `await lsp_service.shutdown_all()` -> stops all LSP clients
        """
        for client in self.clients.values():
            try:
                await client.__aexit__(None, None, None)
            except Exception as e:
                self.app["log"].error(f"Error shutting down LSP client: {e}")

        self.clients.clear()
