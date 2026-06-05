from typing import Any

import websockets.exceptions

from byte import CommandRegistryService
from byte.gateway.protocol import (
    ERR_INTERNAL,
    ERR_METHOD_NOT_FOUND,
    RpcNotification,
    RpcRequest,
    RpcResponse,
    make_error_response,
)
from byte.support import Service


class SessionService(Service):
    """Handle a single authenticated WebSocket session — receive commands and stream events."""

    def boot(
        self,
        websocket: Any,  # websockets does not export a stable ServerConnection type
    ) -> None:
        self._websocket = websocket
        self._command_registry = self.app.make(CommandRegistryService)
        self._subscriptions: list[Any] = []

    async def _send(self, message: RpcResponse | RpcNotification) -> None:
        """Serialize and send a message over the WebSocket, ignoring closed connection errors."""
        try:
            await self._websocket.send(message.model_dump_json())
        except websockets.exceptions.ConnectionClosed:
            pass

    async def _handle_execute(self, request: RpcRequest) -> None:
        """Execute a slash-command or plain text input on behalf of the remote client."""
        params = request.params or {}
        user_input: str = params.get("input", "")

        if not user_input:
            await self._send(make_error_response(request.id, ERR_INTERNAL, "Missing required param: input"))
            return

        try:
            # Mirror exactly how TUIManagerService routes user input
            if user_input.startswith("/"):
                parts = user_input[1:].split(" ", 1)
                command_name = parts[0]
                args = parts[1] if len(parts) > 1 else ""
                command = self._command_registry.get_slash_command(command_name)
                if command:
                    await command.handle(args)
            else:
                command = self._command_registry.get_slash_command("coder")
                if command:
                    await command.handle(user_input)

            await self._send(RpcResponse(id=request.id, result={"ok": True}))
        except Exception as exc:
            self.app["log"].exception("Gateway execute error")
            await self._send(make_error_response(request.id, ERR_INTERNAL, str(exc)))

    async def _dispatch(self, raw: str) -> None:
        """Parse a raw JSON string as an RpcRequest and route to the correct handler."""
        try:
            request = RpcRequest.model_validate_json(raw)
        except Exception:
            await self._send(make_error_response(None, ERR_INTERNAL, "Invalid request"))
            return

        if request.method == "execute":
            await self._handle_execute(request)
        else:
            await self._send(make_error_response(request.id, ERR_METHOD_NOT_FOUND, f"Unknown method: {request.method}"))

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
