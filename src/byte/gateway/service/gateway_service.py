import asyncio
import json
import os
import secrets
from pathlib import Path
from typing import Any

import websockets
import websockets.exceptions
from textual.message import Message

from byte.gateway.protocol import (
    ERR_UNAUTHORIZED,
    RpcRequest,
    RpcResponse,
)
from byte.gateway.service.session_service import SessionService
from byte.gateway.utils import GatewayUtils
from byte.support import Service
from byte.tui import Status
from byte.tui.messages import Messages


class GatewayService(Service):
    """Manage the WebSocket server lifecycle and per-connection auth handshake."""

    def boot(self) -> None:
        self._config = self.app["config"].gateway
        self._token: str = ""
        self._server: Any | None = None  # websockets does not export a stable ServerConnection type
        self._session: SessionService | None = None
        self._actual_port: int = 0

    def _token_path(self) -> Path:
        """Return the path to the gateway token file."""
        return self.app.cache_path("gateway.token")

    def _discovery_path(self) -> Path:
        """Return the path to the gateway discovery file."""
        return self.app.cache_path("gateway.json")

    def _write_token_file(self) -> None:
        """Write the auth token to disk with restricted permissions."""
        path = self._token_path()
        path.write_text(self._token)
        os.chmod(path, 0o600)
        self.app["log"].info(f"Token generated and written to {path}")

    def _write_discovery_file(self) -> None:
        """Write the gateway discovery JSON so external clients can locate the server."""
        data = {
            "host": self._config.host,
            "port": self._actual_port,
            "pid": os.getpid(),
            "token_file": str(self._token_path().resolve()),
        }
        self._discovery_path().write_text(json.dumps(data))

    async def _handle_new_connection(self, websocket: Any) -> None:
        """Perform auth handshake and, on success, hand off to SessionService."""
        self.app["log"].debug("New connection received")
        try:
            raw = await websocket.recv()
            request = RpcRequest.model_validate_json(raw)
        except Exception:
            self.app["log"].warning("Auth failure: malformed request")
            await websocket.send(
                GatewayUtils.make_error_response(None, ERR_UNAUTHORIZED, "Auth required").model_dump_json()
            )
            await websocket.close()
            return

        if request.method != "auth" or not isinstance(request.params, dict):
            self.app["log"].warning("Auth failure: invalid auth method or params")
            await websocket.send(
                GatewayUtils.make_error_response(request.id, ERR_UNAUTHORIZED, "Auth required").model_dump_json()
            )
            await websocket.close()
            return

        if request.params.get("token") != self._token:
            self.app["log"].warning("Auth failure: invalid token")
            await websocket.send(
                GatewayUtils.make_error_response(request.id, ERR_UNAUTHORIZED, "Invalid token").model_dump_json()
            )
            await websocket.close()
            return

        # Auth passed — send OK and create session
        self.app["log"].debug("Auth successful")

        ok_response = RpcResponse(id=request.id, result={"ok": True})
        await websocket.send(ok_response.model_dump_json())

        self._session = self.app.make(SessionService, websocket=websocket)
        await self._session.handle_connection()

    async def start(self) -> None:
        """Generate the auth token, write discovery files, and start the WebSocket server."""
        self._token = secrets.token_urlsafe(32)
        self._write_token_file()

        self.app["log"].info(f"Gateway server starting on {self._config.host}:{self._config.port}")
        self._server = await websockets.serve(
            self._handle_new_connection,
            self._config.host,
            self._config.port,
        )
        sock = self._server.sockets[0]
        self._actual_port = sock.getsockname()[1]
        self._write_discovery_file()
        self.app["log"].info(f"Gateway server running on {self._config.host}:{self._actual_port}")
        await self._server.wait_closed()

    def _cleanup_files(self) -> None:
        """Remove the token and discovery files on shutdown."""
        self.app["log"].info("Cleaning up gateway files")
        for path in (self._token_path(), self._discovery_path()):
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass

    async def stop(self) -> None:
        """Close the WebSocket server and remove discovery files."""
        self.app["log"].info("Gateway server stopping")
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
        self._cleanup_files()

    def post_message(self, event: Message) -> None:
        """Route inbound application events to appropriate notification handlers."""

        if not self._session:
            return

        match event:
            case Messages.Response():
                coroutine = self._session.notify(
                    "messages/response", {"content": str(event.chunk), "done": event.status is Status.SUCCESS}
                )
            case Messages.UpdateFiles():
                coroutine = self._session.notify("messages/update_files", {"count": event.count})
            case Messages.UpdateContext():
                coroutine = self._session.notify("messages/update_context", {"context_count": event.context_count})
            case Messages.CommandExecutionStarted():
                coroutine = self._session.notify("messages/command_execution_started", {})
            case Messages.CommandExecutionCompleted():
                coroutine = self._session.notify("messages/command_execution_completed", {})
            case Messages.Status() if event.state == "error":
                coroutine = self._session.notify("messages/status", {"message": event.message or ""})
            case _:
                return

        asyncio.create_task(coroutine)
