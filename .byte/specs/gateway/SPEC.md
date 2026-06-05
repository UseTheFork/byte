---
description: A new `src/byte/gateway/` domain that exposes a localhost WebSocket server
  using JSON-RPC 2.0, allowing external clients (e.g., a VS Code extension) to send
  commands to and receive streamed responses from a running Byte instance.
name: Gateway Domain — WebSocket JSON-RPC Bridge
reference_files:
  - src/byte/config/byte_config.py
  - src/byte/support/service_provider.py
  - src/byte/support/service.py
  - src/byte/git/service_provider.py
  - src/byte/git/__init__.py
  - src/byte/command/service/command_registry_service.py
  - src/byte/command/command.py
  - src/byte/tui/service/tui_manager_service.py
  - src/byte/tui/widgets/conversation.py
  - src/byte/llm/config.py
  - src/byte/tui/config.py
  - src/byte/foundation/bootstrap/prepare_environment.py
  - src/byte/foundation/bootstrap/load_configuration.py
---

## Overview

Introduce a `gateway` bounded-context domain at `src/byte/gateway/`. The gateway runs an optional WebSocket server on localhost alongside the TUI. External clients (e.g., a VS Code extension) connect, authenticate with a per-boot token, send slash-commands, and receive streamed response events in real time via JSON-RPC 2.0 notifications. The TUI is unaffected — both consumers read from the same `EventBus`.

The feature is **opt-in**: if `gateway.enable` is `false` (the default), nothing starts.

---

## Domain File Map

```
src/byte/gateway/
├── __init__.py
├── config.py
├── protocol.py
├── provider.py
└── service/
    ├── __init__.py
    ├── gateway_service.py
    └── session_service.py
```

---

## 1. `config.py`

Define `GatewayConfig` as a Pydantic `BaseModel` (follow the pattern in `src/byte/llm/config.py` and `src/byte/tui/config.py`).

```python
class GatewayConfig(BaseModel):
    enable: bool = False
    host: str = "127.0.0.1"
    port: int = 9731
```

**Integration**: Add a `gateway: GatewayConfig = GatewayConfig()` field to `ByteUserConfig` in `src/byte/config/byte_config.py`. Follow how `llm` and `tui` fields are declared there. The field must also be listed in `ByteUserConfig.model_fields` so it is serialized to `config.jsonc`.

---

## 2. `protocol.py`

Define strict Pydantic models for the JSON-RPC 2.0 envelope. All models must have `model_config = ConfigDict(extra="forbid")`.

### Inbound (client → gateway)

```python
class RpcRequest(BaseModel):
    jsonrpc: Literal["2.0"]
    id: str | int
    method: str          # e.g. "execute"
    params: dict[str, Any] | None = None
```

**Supported methods** (validated inside `SessionService`):

| Method    | `params` keys | Description                                               |
| --------- | ------------- | --------------------------------------------------------- |
| `execute` | `input: str`  | Run a slash-command or plain text as if typed by the user |

### Outbound (gateway → client)

```python
class RpcResponse(BaseModel):
    """Final result for a request id."""
    jsonrpc: Literal["2.0"]
    id: str | int
    result: dict[str, Any] | None = None
    error: RpcError | None = None

class RpcError(BaseModel):
    code: int
    message: str
    data: Any | None = None

class RpcNotification(BaseModel):
    """Streaming event with no id."""
    jsonrpc: Literal["2.0"]
    method: str       # e.g. "stream/response", "stream/tool", "stream/done"
    params: dict[str, Any]
```

**Error codes** — define as module-level integer constants:

| Constant               | Value    | Meaning                   |
| ---------------------- | -------- | ------------------------- |
| `ERR_PARSE`            | `-32700` | Malformed JSON            |
| `ERR_INVALID_REQUEST`  | `-32600` | Schema validation failure |
| `ERR_METHOD_NOT_FOUND` | `-32601` | Unknown method            |
| `ERR_UNAUTHORIZED`     | `-32000` | Missing or wrong token    |
| `ERR_INTERNAL`         | `-32001` | Unexpected server error   |

Provide a module-level helper:

```python
def make_error_response(id: str | int | None, code: int, message: str) -> RpcResponse: ...
```

---

## 3. `service/gateway_service.py`

`GatewayService` extends `src/byte/support/service.py`'s `Service` base class.

### Responsibilities

1. **Token generation** — on `boot()`, generate a 32-byte URL-safe random token (`secrets.token_urlsafe(32)`). Write it to `app.config_path("gateway.token")` (mode `0o600`).
2. **Discovery file** — write `app.config_path("gateway.json")` with:
   ```json
   { "port": <int>, "pid": <int>, "token_file": "<absolute path to gateway.token>" }
   ```
3. **WebSocket server** — start an `asyncio`-compatible WebSocket server on `config.gateway.host : config.gateway.port` using the `websockets` library (`websockets.serve`). Each accepted connection is handed to `SessionService.handle_connection`.
4. **Cleanup** — on shutdown (SIGTERM / SIGINT or application teardown), close the server, delete `gateway.json` and `gateway.token`.

### Auth handshake

The very first message on any new WebSocket connection MUST be a valid `RpcRequest` with `method = "auth"` and `params = { "token": "<token>" }`. If validation fails or the token does not match, send an `RpcResponse` with `ERR_UNAUTHORIZED` and close the connection. On success, send `RpcResponse(id=<request id>, result={"ok": true})` and hand off to the session loop.

### Key signature

```python
class GatewayService(Service):
    def __init__(self, app: Application, config: GatewayConfig) -> None: ...
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
```

`start()` is called by `GatewayServiceProvider.boot()` inside a background `asyncio` task so it does not block the TUI event loop. Use `asyncio.get_event_loop().create_task(self.start())` or equivalent.

---

## 4. `service/session_service.py`

`SessionService` extends `Service`. One instance is created **per authenticated WebSocket connection** by `GatewayService`.

### Responsibilities

1. **Receive loop** — read inbound JSON messages from the WebSocket, parse as `RpcRequest`, dispatch to the appropriate handler.
2. **`execute` handler** — call `CommandRegistryService.handle_input(params["input"])` exactly as `TuiManagerService` does for keyboard input. This reuses the existing command pipeline with no new API.
3. **EventBus subscription** — subscribe to the following `Messages.*` events on the application `EventBus` for the lifetime of the connection and forward them as `RpcNotification` messages:

| EventBus event          | `RpcNotification.method` | Forwarded `params` fields          |
| ----------------------- | ------------------------ | ---------------------------------- |
| `Messages.Response`     | `stream/response`        | `{ "content": str, "done": bool }` |
| `Messages.ToolResponse` | `stream/tool`            | `{ "tool": str, "content": str }`  |
| `Messages.Done`         | `stream/done`            | `{}`                               |
| `Messages.Error`        | `stream/error`           | `{ "message": str }`               |

> Inspect `src/byte/tui/widgets/conversation.py` for the exact `Messages.*` class shapes to map to the above.

4. **Send helper** — serializes an `RpcNotification` or `RpcResponse` to JSON and sends it over the WebSocket. Must handle `websockets.ConnectionClosed` gracefully.
5. **Cleanup** — on disconnect or error, unsubscribe EventBus handlers and log the disconnection.

### Key signature

```python
class SessionService(Service):
    def __init__(
        self,
        app: Application,
        websocket: Any,          # websockets.ServerConnection
        command_registry: CommandRegistryService,
    ) -> None: ...

    async def handle_connection(self) -> None: ...
```

---

## 5. `provider.py`

`GatewayServiceProvider` extends `src/byte/support/service_provider.py`'s `ServiceProvider`. Follow `src/byte/git/service_provider.py` as the reference implementation.

```python
class GatewayServiceProvider(ServiceProvider):
    def register(self) -> None:
        # Bind GatewayService as a singleton in the container
        self.app.singleton(GatewayService, lambda app: GatewayService(app, app["config"].gateway))

    def boot(self) -> None:
        # Only start if gateway.enable is True
        if not self.app["config"].gateway.enable:
            return
        gateway: GatewayService = self.app[GatewayService]
        # Schedule async start without blocking
        import asyncio
        loop = asyncio.get_event_loop()
        loop.create_task(gateway.start())
```

---

## 6. `__init__.py`

Use the `_dynamic_imports` lazy-import pattern from `src/byte/git/__init__.py`. Export:

- `GatewayConfig`
- `GatewayServiceProvider`
- `GatewayService`
- `SessionService`

---

## 7. Bootstrap integration

### `PrepareEnvironment` (`src/byte/foundation/bootstrap/prepare_environment.py`)

No changes needed — `GatewayService.start()` handles its own file creation at runtime.

### `LoadConfiguration` (`src/byte/foundation/bootstrap/load_configuration.py`)

No changes needed — `GatewayConfig` is a field on `ByteUserConfig` and will be deserialized automatically by the existing `ByteConfig(**user_config)` call.

### Application provider registration

Register `GatewayServiceProvider` in the application's provider list (wherever other domain providers such as the Git provider are registered). The exact file will be visible in the codebase — look for the list of `ServiceProvider` subclasses passed to the application bootstrapper.

---

## 8. Constraints & conventions

- All type annotations are mandatory on every function/method signature (constitution: `strict-typing`).
- All public classes and methods require a one-line imperative docstring (constitution: `minimal-lean-docstrings`).
- No logic duplication — auth token generation lives only in `GatewayService`; JSON-RPC envelope construction lives only in `protocol.py` (constitution: `don-t-repeat-yourself-dry`).
- Cross-domain access only through public interfaces — `SessionService` calls `CommandRegistryService` via its public `handle_input` method; it subscribes to `EventBus` via its public subscription API (constitution: `domain-driven-design`).
- `Any` is only permitted for the `websockets.ServerConnection` parameter until `websockets` ships a stable typed API; annotate with a `# websockets does not export a stable ServerConnection type` comment.
