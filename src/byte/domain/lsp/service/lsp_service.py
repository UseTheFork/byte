from pathlib import Path
from typing import Any, Dict, List, Optional

from byte.core.logging import log
from byte.core.service.base_service import Service
from byte.core.task_manager import TaskManager
from byte.core.utils import get_language_from_filename
from byte.domain.lsp.schemas import (
    CompletionItem,
    Diagnostic,
    HoverResult,
    Location,
)
from byte.domain.lsp.service.lsp_client import LSPClient


class LSPService(Service):
    """Service for managing multiple LSP servers and providing code intelligence.

    Manages LSP client lifecycle, routes requests to appropriate servers based on
    file languages, and provides a unified interface for code intelligence features.
    Usage: `hover = await lsp_service.get_hover(file_path, line, char)` -> hover info
    """

    async def boot(self) -> None:
        """Initialize LSP service with configured servers."""
        self.clients: Dict[str, LSPClient] = {}
        self.language_map: Dict[str, str] = {}
        self.task_manager = await self.make(TaskManager)

        # Build language to server name mapping
        for server_name, server_config in self._config.lsp.servers.items():
            for language in server_config.languages:
                # Store languages in lowercase for case-insensitive matching
                self.language_map[language.lower()] = server_name

        # Start LSP servers in background if enabled
        if self._config.lsp.enable:
            await self._start_lsp_servers()

    async def handle(self, **kwargs) -> Any:
        """Handle LSP service operations.

        Usage: `await lsp_service.handle(operation="hover", file_path=path, line=10, character=5)`
        """
        operation = kwargs.get("operation")
        file_path = kwargs.get("file_path")

        if not operation or not file_path:
            return None

        client = await self._get_client_for_file(file_path)
        if not client:
            return None

        # Ensure document is opened before making requests
        await self._ensure_document_open(client, file_path)

        if operation == "hover":
            return await client.get_hover(file_path, kwargs.get("line", 0), kwargs.get("character", 0))
        elif operation == "references":
            return await client.find_references(file_path, kwargs.get("line", 0), kwargs.get("character", 0))
        elif operation == "definition":
            return await client.goto_definition(file_path, kwargs.get("line", 0), kwargs.get("character", 0))
        elif operation == "declaration":
            return await client.goto_declaration(file_path, kwargs.get("line", 0), kwargs.get("character", 0))
        elif operation == "type_definition":
            return await client.goto_type_definition(file_path, kwargs.get("line", 0), kwargs.get("character", 0))
        elif operation == "signature_help":
            return await client.get_signature_help(file_path, kwargs.get("line", 0), kwargs.get("character", 0))
        elif operation == "completions":
            return await client.get_completions(file_path, kwargs.get("line", 0), kwargs.get("character", 0))

        return None

    async def get_hover(self, file_path: Path, line: int, character: int) -> Optional[HoverResult]:
        """Get hover information for any supported file.

        Usage: `await lsp_service.get_hover(Path("src/main.ts"), 10, 5)` -> hover info
        """
        client = await self._get_client_for_file(file_path)
        if not client:
            return None

        await self._ensure_document_open(client, file_path)
        return await client.get_hover(file_path, line, character)

    async def find_references(self, file_path: Path, line: int, character: int) -> List[Location]:
        """Find references for any supported file.

        Usage: `await lsp_service.find_references(Path("src/main.ts"), 10, 5)` -> list of locations
        """
        client = await self._get_client_for_file(file_path)
        if not client:
            return []

        await self._ensure_document_open(client, file_path)
        return await client.find_references(file_path, line, character)

    async def goto_definition(self, file_path: Path, line: int, character: int) -> List[Location]:
        """Go to definition for any supported file.

        Usage: `await lsp_service.goto_definition(Path("src/main.ts"), 10, 5)` -> definition locations
        """
        client = await self._get_client_for_file(file_path)
        if not client:
            return []

        await self._ensure_document_open(client, file_path)
        return await client.goto_definition(file_path, line, character)

    async def get_completions(self, file_path: Path, line: int, character: int) -> List[CompletionItem]:
        """Get completions for any supported file.

        Usage: `await lsp_service.get_completions(Path("src/main.ts"), 10, 5)` -> completion items
        """
        client = await self._get_client_for_file(file_path)
        if not client:
            return []

        await self._ensure_document_open(client, file_path)
        return await client.get_completions(file_path, line, character)

    async def goto_declaration(self, file_path: Path, line: int, character: int) -> List[Location]:
        """Go to declaration for any supported file.

        Usage: `await lsp_service.goto_declaration(Path("src/main.ts"), 10, 5)` -> declaration locations
        """
        client = await self._get_client_for_file(file_path)
        if not client:
            return []

        await self._ensure_document_open(client, file_path)
        return await client.goto_declaration(file_path, line, character)

    async def goto_type_definition(self, file_path: Path, line: int, character: int) -> List[Location]:
        """Go to type definition for any supported file.

        Usage: `await lsp_service.goto_type_definition(Path("src/main.ts"), 10, 5)` -> type definition locations
        """
        client = await self._get_client_for_file(file_path)
        if not client:
            return []

        await self._ensure_document_open(client, file_path)
        return await client.goto_type_definition(file_path, line, character)

    async def get_signature_help(self, file_path: Path, line: int, character: int) -> Optional[Dict[str, Any]]:
        """Get signature help for any supported file.

        Usage: `await lsp_service.get_signature_help(Path("src/main.ts"), 10, 5)` -> signature help info
        """
        client = await self._get_client_for_file(file_path)
        if not client:
            return None

        await self._ensure_document_open(client, file_path)
        return await client.get_signature_help(file_path, line, character)

    async def get_diagnostics(self, file_path: Path) -> List[Diagnostic]:
        """Get diagnostics for any supported file.

        Usage: `await lsp_service.get_diagnostics(Path("src/main.ts"))` -> list of diagnostics
        """
        client = await self._get_client_for_file(file_path)
        if not client:
            return []

        await self._ensure_document_open(client, file_path)
        return client.get_diagnostics(file_path)

    async def shutdown_all(self) -> None:
        """Shutdown all running LSP servers.

        Usage: `await lsp_service.shutdown_all()` -> stops all LSP clients
        """
        for client in self.clients.values():
            await client.stop()

        self.clients.clear()

    async def _start_lsp_servers(self) -> None:
        """Start all configured LSP servers in background."""
        for server_name, server_config in self._config.lsp.servers.items():
            self.task_manager.start_task(f"lsp_server_{server_name}", self._start_lsp_client(server_name))

    async def _start_lsp_client(self, server_name: str) -> None:
        """Start a single LSP client in background."""
        try:
            server_config = self._config.lsp.servers[server_name]
            client = LSPClient(
                name=server_name,
                command=server_config.command,
                root_path=self._config.project_root,
            )

            log.info(f"Starting LSP server: {server_name}")
            if await client.start():
                self.clients[server_name] = client
                log.info(f"LSP server started successfully: {server_name}")
            else:
                log.error(f"Failed to start LSP server: {server_name}")
        except Exception as e:
            log.error(f"Error starting LSP server {server_name}: {e}")
            log.exception(e)

    async def _get_client_for_file(self, file_path: Path) -> Optional[LSPClient]:
        """Get an LSP client for the given file.

        Usage: Internal method to route file to appropriate LSP server
        """
        if not self._config.lsp.enable:
            return None

        # Get the language for this file using Pygments
        file_language = get_language_from_filename(str(file_path))

        if not file_language:
            log.debug(f"Could not determine language for file: {file_path}")
            return None

        # Determine server from file language (case-insensitive)
        server_name = self.language_map.get(file_language.lower())

        if not server_name or server_name not in self._config.lsp.servers:
            log.debug(f"No LSP server configured for language '{file_language}' (file: {file_path})")
            return None

        # Return existing client if available
        client = self.clients.get(server_name)
        if client:
            return client

        # If client not ready yet, log a warning
        log.warning(f"LSP client '{server_name}' not ready yet for file: {file_path}")
        return None

    async def _ensure_document_open(self, client: LSPClient, file_path: Path) -> bool:
        """Ensure a document is opened in the LSP server.

        Usage: Internal method to notify server about document before requests
        """
        try:
            # Read file content
            content = file_path.read_text(encoding="utf-8")

            # Determine language ID from filename
            file_language = get_language_from_filename(str(file_path))
            if not file_language:
                # Fallback to extension if language detection fails
                language_id = file_path.suffix.lstrip(".")
            else:
                # Use lowercase language name as language ID
                language_id = file_language.lower()

            # Notify server about the document
            await client.did_open(file_path, content, language_id)
            log.debug(f"Opened document in LSP: {file_path}")
            return True
        except Exception as e:
            log.error(f"Failed to open document in LSP: {file_path} - {e}")
            return False
