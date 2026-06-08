from pathlib import Path
from typing import Any, Callable

import websockets.exceptions

from byte import CommandRegistryService
from byte.files.service.file_service import FileService
from byte.gateway.protocol import (
    ERR_INTERNAL,
    ERR_METHOD_NOT_FOUND,
    RpcNotification,
    RpcRequest,
    RpcResponse,
)
from byte.gateway.requests import GatewayRequest, Requests
from byte.gateway.utils import GatewayUtils, on
from byte.knowledge import SessionContextModel, SessionContextService
from byte.support import Service


class SessionService(Service):
    """Handle a single authenticated WebSocket session — receive commands and stream events."""

    def _build_dispatch_table(self) -> None:
        """Scan methods for `_gateway_request_type` attribute and build dispatch table."""
        self._handlers: dict[type[GatewayRequest], Callable] = {}
        for method_name in dir(self):
            try:
                method = getattr(self, method_name)
            except AttributeError:
                continue
            if callable(method) and hasattr(method, "_gateway_request_type"):
                request_type: type[GatewayRequest] = getattr(method, "_gateway_request_type")
                self._handlers[request_type] = method

    def boot(
        self,
        websocket: Any,  # websockets does not export a stable ServerConnection type
    ) -> None:
        self._websocket = websocket
        self._command_registry = self.app.make(CommandRegistryService)
        self._subscriptions: list[Any] = []
        self._build_dispatch_table()

    async def _send(self, message: RpcResponse | RpcNotification) -> None:
        """Serialize and send a message over the WebSocket, ignoring closed connection errors."""
        try:
            await self._websocket.send(message.model_dump_json())
        except websockets.exceptions.ConnectionClosed:
            pass

    @on(Requests.AddFile)
    async def handle_add_file(self, request: Requests.AddFile) -> None:
        file_service = self.app.make(FileService)
        result = await file_service.add_file(request.file_path)

        if not result:
            await self._send(
                GatewayUtils.make_error_response(
                    request.id,
                    ERR_INTERNAL,
                    f"Failed to add {request.file_path} (file not found, not readable, or already in context)",
                )
            )
            return

        await file_service.notify_file_stats()
        await self._send(RpcResponse(id=request.id, result={"ok": True, "file_path": request.file_path}))

    @on(Requests.DropFile)
    async def handle_drop_file(self, request: Requests.DropFile) -> None:
        file_service = self.app.make(FileService)
        result = await file_service.remove_file(request.file_path)

        if not result:
            await self._send(
                GatewayUtils.make_error_response(
                    request.id,
                    ERR_INTERNAL,
                    f"Failed to remove {request.file_path} (file not found, not readable, or already in context)",
                )
            )
            return

        await file_service.notify_file_stats()
        await self._send(RpcResponse(id=request.id, result={"ok": True, "file_path": request.file_path}))

    @on(Requests.ContextAddFile)
    async def handle_context_add_file(self, request: Requests.ContextAddFile) -> None:
        session_context_service = self.app.make(SessionContextService)

        file_path = Path(request.file_path)
        if not file_path.is_absolute():
            file_path = self.app.root_path(str(file_path))

        if not file_path.exists():
            await self._send(
                GatewayUtils.make_error_response(
                    request.id,
                    ERR_INTERNAL,
                    f"File not found: {request.file_path}",
                )
            )
            return

        if not file_path.is_file():
            await self._send(
                GatewayUtils.make_error_response(
                    request.id,
                    ERR_INTERNAL,
                    f"Path is not a file: {request.file_path}",
                )
            )
            return

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            await self._send(
                GatewayUtils.make_error_response(
                    request.id,
                    ERR_INTERNAL,
                    f"Error reading file: {e!s}",
                )
            )
            return

        context_key = str(file_path.relative_to(self.app["path"]))
        model = self.app.make(SessionContextModel, type="file", key=context_key, content=content)
        session_context_service.add_context(model)

        await self._send(RpcResponse(id=request.id, result={"ok": True, "file_path": request.file_path}))

    async def _dispatch(self, raw: str) -> None:
        """Parse a raw JSON string as an RpcRequest and route to the correct handler."""
        try:
            rpc = RpcRequest.model_validate_json(raw)
        except Exception:
            await self._send(GatewayUtils.make_error_response(None, ERR_INTERNAL, "Invalid request"))
            return

        try:
            request = GatewayUtils.parse_request(rpc)
        except ValueError as exc:
            await self._send(GatewayUtils.make_error_response(rpc.id, ERR_METHOD_NOT_FOUND, str(exc)))
            return

        handler = self._handlers.get(type(request))
        if handler is None:
            await self._send(GatewayUtils.make_error_response(request.id, ERR_METHOD_NOT_FOUND, "Unknown method type"))
            return

        await handler(request)

    async def notify(self, method: str, params: dict[str, Any]) -> None:
        """Build and send an RpcNotification for the given method and params."""
        await self._send(RpcNotification(method=method, params=params))

    async def handle_connection(self) -> None:
        """Subscribe to EventBus events and run the inbound message loop until the client disconnects."""
        try:
            self.app["log"].debug("Gateway started")
            async for raw in self._websocket:
                await self._dispatch(raw)
        except websockets.exceptions.ConnectionClosed:
            self.app["log"].debug("Gateway client disconnected")
        finally:
            pass
