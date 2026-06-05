---
files:
  create:
  - src/byte/gateway/service/session_service.py
  edit: []
  reference:
  - src/byte/support/service.py
  - src/byte/tui/widgets/conversation.py
  - src/byte/tui/service/tui_manager_service.py
  - src/byte/command/service/command_registry_service.py
  - src/byte/gateway/protocol.py
id: create-session-service
notes: []
order: 5
status: completed
---
# Gateway Domain — `service/session_service.py`
**Goal:** Implement the per-connection session that receives RPC requests, dispatches commands, and forwards EventBus events back to the client as JSON-RPC notifications.
**Architecture:** `SessionService` extends `Service`. One instance is created per authenticated connection by `GatewayService`. It subscribes to the application `EventBus` for the connection lifetime and unsubscribes on disconnect. Command execution delegates entirely to `CommandRegistryService.handle_input` — no new command logic here.

---

## Create `src/byte/gateway/service/session_service.py`

### Imports

```python
import asyncio
import json
import logging
from typing import TYPE_CHECKING, Any

import websockets.exceptions

from byte.gateway.protocol import (
    ERR_INTERNAL,
    ERR_METHOD_NOT_FOUND,
    RpcNotification,
    RpcRequest,
    RpcResponse,
    make_error_response,
)
from byte.support import Service

if TYPE_CHECKING:
    from byte.command.service.command_registry_service import CommandRegistryService
    from byte.foundation import Application

log = logging.getLogger(__name__)
```

### Class skeleton

```python
class SessionService(Service):
    """Handle a single authenticated WebSocket session — receive commands and stream events."""

    def __init__(
        self,
        app: Application,
        websocket: Any,  # websockets does not export a stable ServerConnection type
        command_registry: CommandRegistryService,
    ) -> None:
        self._app = app
        self._websocket = websocket
        self._command_registry = command_registry
        self._subscriptions: list[Any] = []
```

### `handle_connection()` — main entry point

```python
    async def handle_connection(self) -> None:
        """Subscribe to EventBus events and run the inbound message loop until the client disconnects."""
        self._subscribe_events()
        try:
            async for raw in self._websocket:
                await self._dispatch(raw)
        except websockets.exceptions.ConnectionClosed:
            log.debug("Gateway client disconnected")
        finally:
            self._unsubscribe_events()
```

### Inbound dispatch

```python
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
            log.exception("Gateway execute error")
            await self._send(make_error_response(request.id, ERR_INTERNAL, str(exc)))
```

### EventBus subscription

Inspect `src/byte/tui/widgets/conversation.py` for the exact `Messages.*` shapes. The four events to forward are:

| `Messages` event | Key attributes to extract | `RpcNotification.method` |
|---|---|---|
| `Messages.Response` | `chunk: str`, `status` (map `RUNNING` → `done=False`, `SUCCESS` → `done=True`) | `stream/response` |
| `Messages.ToolResponse` | `tool_name: str`, `chunk: str` | `stream/tool` |
| `Messages.CommandExecutionCompleted` | *(none)* | `stream/done` |
| `Messages.Status` with `state="error"` | `message: str` | `stream/error` |

```python
    def _subscribe_events(self) -> None:
        """Subscribe to application EventBus events for the lifetime of this session."""
        from byte import EventBus
        from byte.tui.messages import Messages
        from byte.tui import Status

        event_bus: EventBus = self._app.make(EventBus)

        async def on_response(event: Messages.Response) -> None:
            done = event.status is Status.SUCCESS
            await self._notify("stream/response", {"content": str(event.chunk), "done": done})

        async def on_tool_response(event: Messages.ToolResponse) -> None:
            await self._notify("stream/tool", {"tool": str(event.tool_name), "content": str(event.chunk)})

        async def on_done(event: Messages.CommandExecutionCompleted) -> None:
            await self._notify("stream/done", {})

        async def on_error(event: Messages.Status) -> None:
            if event.state == "error":
                await self._notify("stream/error", {"message": event.message or ""})

        self._subscriptions = [
            event_bus.subscribe(Messages.Response, on_response),
            event_bus.subscribe(Messages.ToolResponse, on_tool_response),
            event_bus.subscribe(Messages.CommandExecutionCompleted, on_done),
            event_bus.subscribe(Messages.Status, on_error),
        ]

    def _unsubscribe_events(self) -> None:
        """Unsubscribe all EventBus handlers registered by this session."""
        from byte import EventBus

        event_bus: EventBus = self._app.make(EventBus)
        for subscription in self._subscriptions:
            event_bus.unsubscribe(subscription)
        self._subscriptions = []
```

> **EventBus API**: Check the actual `EventBus` class in `src/byte/` for the exact `subscribe` / `unsubscribe` method signatures. The pattern above mirrors how the `Conversation` widget uses the bus. Adjust subscription token handling to match whatever the `EventBus` returns from `subscribe`.

### Send helpers

```python
    async def _send(self, message: RpcResponse | RpcNotification) -> None:
        """Serialize and send a message over the WebSocket, ignoring closed connection errors."""
        try:
            await self._websocket.send(message.model_dump_json())
        except websockets.exceptions.ConnectionClosed:
            pass

    async def _notify(self, method: str, params: dict[str, Any]) -> None:
        """Build and send an RpcNotification for the given method and params."""
        await self._send(RpcNotification(method=method, params=params))
```
