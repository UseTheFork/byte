---
files:
  create:
  - src/byte/gateway/service/__init__.py
  - src/byte/gateway/service/gateway_service.py
  edit: []
  reference:
  - src/byte/support/service.py
  - src/byte/tui/service/tui_manager_service.py
  - src/byte/foundation/bootstrap/prepare_environment.py
  - src/byte/gateway/protocol.py
  - src/byte/gateway/config.py
id: create-gateway-service
notes: []
order: 4
status: completed
---
# Gateway Domain — `service/gateway_service.py`

**Goal:** Implement the WebSocket server that manages per-boot token generation, discovery file writing, connection acceptance with auth handshake, and clean shutdown.
**Architecture:** `GatewayService` extends `Service`. It owns the `websockets` server lifecycle and delegates authenticated connections to `SessionService`. Auth logic lives here exclusively — no other class generates or validates the token.

---

## Create `src/byte/gateway/service/__init__.py`

Empty file — required for Python to treat `service/` as a package.

## Create `src/byte/gateway/service/gateway_service.py`

### Imports

```python
import asyncio
import json
import os
import secrets
from typing import TYPE_CHECKING, Any

import websockets
import websockets.exceptions

from byte.gateway.config import GatewayConfig
from byte.gateway.protocol import ERR_UNAUTHORIZED, RpcRequest, make_error_response
from byte.support import Service

if TYPE_CHECKING:
    from byte.foundation import Application
```

### Class skeleton

```python
class GatewayService(Service):
    """Manage the WebSocket server lifecycle and per-connection auth handshake."""

    def __init__(self, app: Application, config: GatewayConfig) -> None:
        self._app = app
        self._config = config
        self._token: str = ""
        self._server: Any | None = None  # websockets does not export a stable ServerConnection type
```

### `start()` method

```python
    async def start(self) -> None:
        """Generate the auth token, write discovery files, and start the WebSocket server."""
        self._token = secrets.token_urlsafe(32)
        self._write_token_file()
        self._write_discovery_file()

        self._server = await websockets.serve(
            self._handle_new_connection,
            self._config.host,
            self._config.port,
        )
        await self._server.wait_closed()
```

### `stop()` method

```python
    async def stop(self) -> None:
        """Close the WebSocket server and remove discovery files."""
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
        self._cleanup_files()
```

### Token and discovery file helpers

```python
    def _token_path(self):
        """Return the path to the gateway token file."""
        return self._app.config_path("gateway.token")

    def _discovery_path(self):
        """Return the path to the gateway discovery file."""
        return self._app.config_path("gateway.json")

    def _write_token_file(self) -> None:
        """Write the auth token to disk with restricted permissions."""
        path = self._token_path()
        path.write_text(self._token)
        os.chmod(path, 0o600)

    def _write_discovery_file(self) -> None:
        """Write the gateway discovery JSON so external clients can locate the server."""
        data = {
            "port": self._config.port,
            "pid": os.getpid(),
            "token_file": str(self._token_path().resolve()),
        }
        self._discovery_path().write_text(json.dumps(data))

    def _cleanup_files(self) -> None:
        """Remove the token and discovery files on shutdown."""
        for path in (self._token_path(), self._discovery_path()):
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
```

### Auth handshake and connection dispatch

```python
    async def _handle_new_connection(self, websocket: Any) -> None:
        """Perform auth handshake and, on success, hand off to SessionService."""
        try:
            raw = await websocket.recv()
            request = RpcRequest.model_validate_json(raw)
        except Exception:
            await websocket.send(make_error_response(None, ERR_UNAUTHORIZED, "Auth required").model_dump_json())
            await websocket.close()
            return

        if request.method != "auth" or not isinstance(request.params, dict):
            await websocket.send(make_error_response(request.id, ERR_UNAUTHORIZED, "Auth required").model_dump_json())
            await websocket.close()
            return

        if request.params.get("token") != self._token:
            await websocket.send(make_error_response(request.id, ERR_UNAUTHORIZED, "Invalid token").model_dump_json())
            await websocket.close()
            return

        # Auth passed — send OK and create session
        from byte.gateway.protocol import RpcResponse
        from byte.gateway.service.session_service import SessionService
        from byte.command.service.command_registry_service import CommandRegistryService

        ok_response = RpcResponse(id=request.id, result={"ok": True})
        await websocket.send(ok_response.model_dump_json())

        command_registry: CommandRegistryService = self._app.make(CommandRegistryService)
        session = SessionService(self._app, websocket, command_registry)
        await session.handle_connection()
```

> **Note on `_app.make` / `_app.config_path`**: Follow exactly the same call patterns used in `TUIManagerService` and `PrepareEnvironment` — these are the established public APIs on `Application`.
