import asyncio
import json
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, Dict, List, Optional

from byte.core.logging import log
from byte.domain.lsp.schemas import (
    CompletionItem,
    Diagnostic,
    HoverResult,
    Location,
    LspServerState,
)


class LSPClient:
    """Client for communicating with a single LSP server process."""

    def __init__(self, name: str, command: List[str], root_path: Path) -> None:
        self.name = name
        self.command = command
        self.root_path = root_path
        self.process: Optional[asyncio.subprocess.Process] = None
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.state = LspServerState.STOPPED
        self.request_id = 0
        self.pending_requests: Dict[int, asyncio.Future] = {}
        self._read_task: Optional[asyncio.Task] = None
        self._stderr_task: Optional[asyncio.Task] = None
        self._opened_documents: set[Path] = set()
        self._diagnostics: Dict[str, List[Diagnostic]] = {}

    async def start(self) -> bool:
        """Start the LSP server process.

        Usage: `await client.start()` -> starts server and initializes
        """
        if self.state == LspServerState.RUNNING:
            log.debug(f"[LSP {self.name}] Already running")
            return True

        log.info(f"[LSP {self.name}] Starting server with command: {' '.join(self.command)}")
        self.state = LspServerState.STARTING

        try:
            self.process = await asyncio.create_subprocess_exec(
                *self.command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            log.debug(f"[LSP {self.name}] Process started with PID {self.process.pid}")

            self.reader = self.process.stdout
            self.writer = self.process.stdin

            # Start reading responses in background
            self._read_task = asyncio.create_task(self._read_loop())

            # Start stderr monitoring
            self._stderr_task = asyncio.create_task(self._read_stderr())

            log.debug(f"[LSP {self.name}] Read task started")

            # Initialize the server
            log.debug(f"[LSP {self.name}] Sending initialize request")
            await self._initialize()
            log.info(f"[LSP {self.name}] Server initialized successfully")

            # State will be set to RUNNING when we receive the initialize response
            return True

        except Exception as e:
            log.error(f"[LSP {self.name}] Failed to start: {e}")
            log.exception(e)
            self.state = LspServerState.FAILED
            return False

    async def stop(self) -> None:
        """Stop the LSP server process.

        Usage: `await client.stop()` -> gracefully shuts down server
        """
        if self.state != LspServerState.RUNNING:
            return

        try:
            # Send shutdown request
            await self._send_request("shutdown", {})
            await self._send_notification("exit", {})
        except Exception:
            pass

        # Cancel read tasks
        if self._read_task:
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                pass

        if self._stderr_task:
            self._stderr_task.cancel()
            try:
                await self._stderr_task
            except asyncio.CancelledError:
                pass

        # Close streams
        if self.writer:
            self.writer.close()
            try:
                await self.writer.wait_closed()
            except Exception:
                pass

        # Terminate process
        if self.process:
            try:
                if self.process.returncode is None:
                    self.process.terminate()
                    await asyncio.wait_for(self.process.wait(), timeout=5.0)
            except (ProcessLookupError, TimeoutError):
                # Process already gone or timeout - try kill
                try:
                    if self.process.returncode is None:
                        self.process.kill()
                except ProcessLookupError:
                    pass  # Already dead
            except Exception as e:
                log.debug(f"[LSP {self.name}] Process cleanup error: {e}")

        self.state = LspServerState.STOPPED

    async def get_hover(self, file_path: Path, line: int, character: int) -> Optional[HoverResult]:
        """Get hover information for a symbol.

        Usage: `await client.get_hover(Path("src/main.ts"), 10, 5)` -> hover info
        """
        response = await self._send_request(
            "textDocument/hover",
            {
                "textDocument": {"uri": file_path.as_uri()},
                "position": {"line": line, "character": character},
            },
        )

        if response and "contents" in response:
            contents = response["contents"]
            content_str = self._extract_hover_content(contents)
            if content_str:
                return HoverResult(contents=content_str)

        return None

    def _extract_hover_content(self, contents: Any) -> Optional[str]:
        """Extract string content from various hover response formats."""
        if isinstance(contents, str):
            return contents
        elif isinstance(contents, dict):
            return contents.get("value", "")
        elif isinstance(contents, list) and contents:
            first = contents[0]
            if isinstance(first, dict):
                return first.get("value", "")
            return str(first)
        return None

    async def find_references(
        self, file_path: Path, line: int, character: int, include_declaration: bool = True
    ) -> List[Location]:
        """Find all references to a symbol.

        Usage: `await client.find_references(Path("src/main.ts"), 10, 5)` -> list of locations
        """
        response = await self._send_request(
            "textDocument/references",
            {
                "textDocument": {"uri": file_path.as_uri()},
                "position": {"line": line, "character": character},
                "context": {"includeDeclaration": include_declaration},
            },
        )

        if response and isinstance(response, list):
            return [Location(**loc) for loc in response]

        return []

    async def goto_definition(self, file_path: Path, line: int, character: int) -> List[Location]:
        """Go to definition of a symbol.

        Usage: `await client.goto_definition(Path("src/main.ts"), 10, 5)` -> definition locations
        """

        response = await self._send_request(
            "textDocument/definition",
            {
                "textDocument": {"uri": file_path.as_uri()},
                "position": {"line": line, "character": character},
            },
        )

        if response:
            if isinstance(response, list):
                return [Location(**loc) for loc in response]
            elif isinstance(response, dict):
                return [Location(**response)]

        return []

    async def goto_declaration(self, file_path: Path, line: int, character: int) -> List[Location]:
        """Go to declaration of a symbol.

        Usage: `await client.goto_declaration(Path("src/main.ts"), 10, 5)` -> declaration locations
        """

        response = await self._send_request(
            "textDocument/declaration",
            {
                "textDocument": {"uri": file_path.as_uri()},
                "position": {"line": line, "character": character},
            },
        )

        if response:
            if isinstance(response, list):
                return [Location(**loc) for loc in response]
            elif isinstance(response, dict):
                return [Location(**response)]

        return []

    async def goto_type_definition(self, file_path: Path, line: int, character: int) -> List[Location]:
        """Go to type definition of a symbol.

        Usage: `await client.goto_type_definition(Path("src/main.ts"), 10, 5)` -> type definition locations
        """

        response = await self._send_request(
            "textDocument/typeDefinition",
            {
                "textDocument": {"uri": file_path.as_uri()},
                "position": {"line": line, "character": character},
            },
        )

        if response:
            if isinstance(response, list):
                return [Location(**loc) for loc in response]
            elif isinstance(response, dict):
                return [Location(**response)]

        return []

    async def get_signature_help(self, file_path: Path, line: int, character: int) -> Optional[Dict[str, Any]]:
        """Get signature help for a function call.

        Usage: `await client.get_signature_help(Path("src/main.ts"), 10, 5)` -> signature help info
        """

        response = await self._send_request(
            "textDocument/signatureHelp",
            {
                "textDocument": {"uri": file_path.as_uri()},
                "position": {"line": line, "character": character},
            },
        )

        return response

    async def get_completions(self, file_path: Path, line: int, character: int) -> List[CompletionItem]:
        """Get completion suggestions.

        Usage: `await client.get_completions(Path("src/main.ts"), 10, 5)` -> completion items
        """
        response = await self._send_request(
            "textDocument/completion",
            {
                "textDocument": {"uri": file_path.as_uri()},
                "position": {"line": line, "character": character},
            },
        )

        if response:
            items = response.get("items", []) if isinstance(response, dict) else response
            if isinstance(items, list):
                return [CompletionItem(**item) for item in items]

        return []

    async def did_open(self, file_path: Path, content: str, language_id: str) -> None:
        """Notify server that a document was opened.

        Usage: `await client.did_open(Path("src/main.ts"), content, "typescript")`
        """
        # Skip if already opened
        if file_path in self._opened_documents:
            log.debug(f"[LSP {self.name}] Document already open: {file_path}")
            return

        await self._send_notification(
            "textDocument/didOpen",
            {
                "textDocument": {
                    "uri": file_path.as_uri(),
                    "languageId": language_id,
                    "version": 1,
                    "text": content,
                }
            },
        )

        self._opened_documents.add(file_path)

    async def did_change(self, file_path: Path, content: str, version: int) -> None:
        """Notify server that a document changed.

        Usage: `await client.did_change(Path("src/main.ts"), new_content, 2)`
        """
        await self._send_notification(
            "textDocument/didChange",
            {
                "textDocument": {"uri": file_path.as_uri(), "version": version},
                "contentChanges": [{"text": content}],
            },
        )

    async def did_close(self, file_path: Path) -> None:
        """Notify server that a document was closed.

        Usage: `await client.did_close(Path("src/main.ts"))`
        """
        await self._send_notification("textDocument/didClose", {"textDocument": {"uri": file_path.as_uri()}})
        self._opened_documents.discard(file_path)

    def get_diagnostics(self, file_path: Path) -> List[Diagnostic]:
        """Get diagnostics for a file.

        Usage: `diagnostics = client.get_diagnostics(Path("src/main.ts"))` -> list of diagnostics
        """
        uri = file_path.as_uri()
        return self._diagnostics.get(uri, [])

    async def _initialize(self) -> None:
        """Send initialize request to LSP server."""
        # Get client version
        try:
            client_version = version("byte-ai-cli")
        except PackageNotFoundError:
            client_version = "dev"

        await self._send_request(
            "initialize",
            {
                "processId": None,
                "rootUri": self.root_path.as_uri(),
                "rootPath": str(self.root_path),
                "clientInfo": {
                    "name": "byte",
                    "version": client_version,
                },
                "capabilities": {
                    "textDocument": {
                        "hover": {"contentFormat": ["markdown", "plaintext"]},
                        "implementation": {"linkSupport": True},
                        "references": {},
                        "definition": {"linkSupport": True},
                        "declaration": {"linkSupport": True},
                        "typeDefinition": {"linkSupport": True},
                        "signatureHelp": {
                            "signatureInformation": {
                                "documentationFormat": ["markdown", "plaintext"],
                                "parameterInformation": {"labelOffsetSupport": True},
                            }
                        },
                        "completion": {
                            "completionItem": {
                                "snippetSupport": True,
                                "documentationFormat": ["markdown", "plaintext"],
                            }
                        },
                    }
                },
            },
        )

        # Send initialized notification
        await self._send_notification("initialized", {})

        # Give the server a moment to finish initialization
        # Some servers send diagnostics and other notifications after initialized
        await asyncio.sleep(0.5)

    async def _send_request(self, method: str, params: Dict[str, Any]) -> Optional[Any]:
        """Send a JSON-RPC request and wait for response."""
        # Allow initialize request during STARTING state
        if self.state == LspServerState.STARTING and method != "initialize":
            log.warning(f"[LSP {self.name}] Cannot send request {method}: server state is {self.state}")
            return None
        elif self.state not in (LspServerState.RUNNING, LspServerState.STARTING):
            log.warning(f"[LSP {self.name}] Cannot send request {method}: server state is {self.state}")
            return None

        self.request_id += 1
        request_id = self.request_id

        message = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params,
        }

        # Create future bound to current event loop
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self.pending_requests[request_id] = future

        log.debug(f"[LSP {self.name}] Sending request #{request_id}: {method}")
        log.debug(f"[LSP {self.name}] Request message: {message}")
        log.debug(f"[LSP {self.name}] Pending requests: {list(self.pending_requests.keys())}")

        # Send request
        try:
            await self._write_message(message)
            log.debug(f"[LSP {self.name}] Request #{request_id} sent successfully")
        except Exception as e:
            log.error(f"[LSP {self.name}] Failed to send request #{request_id}: {e}")
            log.exception(e)
            self.pending_requests.pop(request_id, None)
            return None

        # Wait for response
        try:
            log.debug(f"[LSP {self.name}] Waiting for response to request #{request_id}...")
            result = await asyncio.wait_for(future, timeout=30.0)
            log.debug(f"[LSP {self.name}] Received response to request #{request_id}")
            return result
        except TimeoutError:
            self.pending_requests.pop(request_id, None)
            log.warning(f"[LSP {self.name}] Request #{request_id} timeout after 30s: {method}")
            log.warning(f"[LSP {self.name}] Still pending: {list(self.pending_requests.keys())}")
            return None
        except Exception as e:
            self.pending_requests.pop(request_id, None)
            log.error(f"[LSP {self.name}] Request #{request_id} failed: {e}")
            log.exception(e)
            return None

    async def _send_notification(self, method: str, params: Dict[str, Any]) -> None:
        """Send a JSON-RPC notification (no response expected)."""
        if self.state != LspServerState.RUNNING:
            return

        message = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
        }

        await self._write_message(message)

    async def _write_message(self, message: Dict[str, Any]) -> None:
        """Write a JSON-RPC message to the server."""
        content = json.dumps(message)
        header = f"Content-Length: {len(content)}\r\n\r\n"
        if self.writer:
            self.writer.write((header + content).encode("utf-8"))
            await self.writer.drain()

    async def _read_loop(self) -> None:
        """Continuously read messages from the server."""
        log.debug(f"[LSP {self.name}] Read loop started")
        try:
            while True:
                log.debug(f"[LSP {self.name}] Waiting for message...")
                message = await self._read_message()
                if message is None:
                    log.warning(f"[LSP {self.name}] Read message returned None, stopping read loop")
                    break

                log.debug(f"[LSP {self.name}] Received message: {message}")

                # Handle response
                if "id" in message and message["id"] in self.pending_requests:
                    request_id = message["id"]
                    future = self.pending_requests.pop(request_id)

                    if "result" in message:
                        log.debug(f"[LSP {self.name}] Setting result for request #{request_id}")

                        # Check if this is the initialize response (request_id == 1)
                        if request_id == 1 and "capabilities" in message["result"]:
                            log.info(f"[LSP {self.name}] Received initialize response, setting state to RUNNING")
                            self.state = LspServerState.RUNNING

                        future.set_result(message["result"])
                    elif "error" in message:
                        log.error(f"[LSP {self.name}] Error response for request #{request_id}: {message['error']}")
                        future.set_exception(Exception(message["error"]))
                elif "id" in message:
                    log.warning(f"[LSP {self.name}] Received response for unknown request #{message['id']}")
                elif "method" in message:
                    # This is a notification from server
                    method = message["method"]
                    log.debug(f"[LSP {self.name}] Received notification: {method}")

                    # Handle publishDiagnostics notification
                    if method == "textDocument/publishDiagnostics":
                        await self._handle_publish_diagnostics(message.get("params", {}))

        except asyncio.CancelledError:
            log.debug(f"[LSP {self.name}] Read loop cancelled")
            pass
        except Exception as e:
            log.error(f"[LSP {self.name}] Read loop error: {e}")
            log.exception(e)
            self.state = LspServerState.FAILED

    async def _handle_publish_diagnostics(self, params: Dict[str, Any]) -> None:
        """Handle publishDiagnostics notification from server."""
        uri = params.get("uri")
        diagnostics_data = params.get("diagnostics", [])

        if uri:
            try:
                # Parse diagnostics
                diagnostics = [Diagnostic(**diag) for diag in diagnostics_data]
                self._diagnostics[uri] = diagnostics
                log.debug(f"[LSP {self.name}] Received {len(diagnostics)} diagnostics for {uri}")
            except Exception as e:
                log.error(f"[LSP {self.name}] Failed to parse diagnostics: {e}")

    async def _read_stderr(self) -> None:
        """Read and log stderr from the LSP server."""
        try:
            while True:
                if self.process is None or self.process.stderr is None:
                    break
                line = await self.process.stderr.readline()
                if not line:
                    break
                log.debug(f"[LSP {self.name}] stderr: {line.decode('utf-8').strip()}")
        except Exception as e:
            log.error(f"[LSP {self.name}] Error reading stderr: {e}")

    async def _read_message(self) -> Optional[Dict[str, Any]]:
        """Read a single JSON-RPC message from the server."""
        try:
            # Read headers
            headers = {}
            while True:
                if self.reader is None:
                    log.warning(f"[LSP {self.name}] Reader is None")
                    return None
                line = await self.reader.readline()
                if not line:
                    log.warning(f"[LSP {self.name}] EOF while reading headers")
                    return None
                if line == b"\r\n":
                    break

                decoded = line.decode("utf-8").strip()
                if ": " in decoded:
                    key, value = decoded.split(": ", 1)
                    headers[key] = value

            # Read content
            if "Content-Length" not in headers:
                log.warning(f"[LSP {self.name}] No Content-Length in headers: {headers}")
                return None

            content_length = int(headers["Content-Length"])
            log.debug(f"[LSP {self.name}] Reading {content_length} bytes of content")

            # Read content in chunks to ensure we get all of it
            content = b""
            remaining = content_length
            while remaining > 0:
                chunk = await self.reader.read(min(remaining, 4096))
                if not chunk:
                    log.warning(
                        f"[LSP {self.name}] EOF while reading content, got {len(content)}/{content_length} bytes"
                    )
                    return None
                content += chunk
                remaining -= len(chunk)

            message = json.loads(content.decode("utf-8"))
            log.debug(f"[LSP {self.name}] Parsed message type: {message.get('method', message.get('id', 'unknown'))}")
            return message

        except Exception as e:
            log.error(f"[LSP {self.name}] Error reading LSP message: {e}")
            log.exception(e)
            return None
