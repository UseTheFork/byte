---
description: Guides development within the gateway domain (src/byte/gateway/) — a
  WebSocket JSON-RPC 2.0 bridge. Covers domain structure, public API boundary, the
  @on dispatch pattern, adding new RPC methods, and cross-domain interaction rules.
name: gateway-domain
---
## When This Skill Applies

Use this skill when:

- Editing or creating files under `src/byte/gateway/` or `src/tests/gateway/`
- Code in another domain needs to push events to connected WebSocket clients
- Adding a new RPC method to the gateway
- Debugging the auth handshake, dispatch routing, or streaming notification flow

---

## Domain Overview

The gateway domain is a **WebSocket JSON-RPC 2.0 bridge** that exposes an authenticated RPC interface for external clients (e.g., editor plugins). It lives entirely under `src/byte/gateway/`.

### File Map

| File | Purpose |
|---|---|
| `config.py` | `GatewayConfig` — `enable`, `host`, `port` settings |
| `protocol.py` | JSON-RPC 2.0 models: `RpcRequest`, `RpcResponse`, `RpcNotification`, `RpcError`, error code constants |
| `requests.py` | Typed request dataclasses: `GatewayRequest` base, `Requests` namespace (`Configure`, `AddFile`, `DropFile`, `ContextAddFile`, `ContextDropFile`) |
| `service/gateway_service.py` | `GatewayService` — server lifecycle, auth handshake, discovery file, event routing via `post_message` |
| `service/session_service.py` | `SessionService` — single-session dispatch loop, `@on`-decorated handlers, `notify()` for outbound notifications |
| `service_provider.py` | `GatewayServiceProvider` — registers singleton, boots server in background task, handles shutdown |
| `utils/dispatch.py` | `@on` decorator — tags methods with `_gateway_request_type` for dispatch table building |
| `utils/gateway_utils.py` | `GatewayUtils` — `parse_request`, `make_error_response`, `REQUEST_TYPES` auto-discovery |

---

## Public API Boundary

The gateway domain exports **only** these symbols from `__init__.py`:

- `GatewayConfig`
- `GatewayService`
- `GatewayServiceProvider`
- `SessionService`

**Everything else is internal.** Types like `RpcRequest`, `RpcResponse`, `RpcNotification`, `RpcError`, `GatewayRequest`, `Requests`, `@on`, and `GatewayUtils` must only be imported within `src/byte/gateway/`.

---

## Cross-Domain Interaction Rules

External domains that need to communicate with connected WebSocket clients **must**:

1. Obtain `GatewayService` from the container
2. Call `gateway_service.post_message(event)` with a Textual `Message` instance
3. Never import internal gateway types (`RpcRequest`, `RpcNotification`, `@on`, `GatewayUtils`, `Requests`)

`GatewayService.post_message` routes application events to the active session's notification stream using pattern matching:

| Event Type | Notification Method | Params |
|---|---|---|
| `Messages.Response` | `stream/response` | `content`, `done` |
| `Messages.ToolResponse` | `stream/tool` | `tool`, `content` |
| `Messages.CommandExecutionCompleted` | `stream/done` | `{}` |
| `Messages.Status` (error) | `stream/error` | `message` |

---

## Adding a New RPC Method

Follow these three steps exactly:

### Step 1 — Define the request dataclass

Add a new dataclass inside the `Requests` namespace in `requests.py`:

```python
@dataclass
class NewMethod(GatewayRequest):
    """Describe what this method does."""
    some_param: str
    optional_param: int | None = None
```

The class name is automatically converted to a snake_case RPC method name (e.g., `NewMethod` becomes `new_method`) via `GatewayUtils.REQUEST_TYPES`.

### Step 2 — Add the handler in SessionService

In `service/session_service.py`, add a method decorated with `@on`:

```python
@on(Requests.NewMethod)
async def handle_new_method(self, request: Requests.NewMethod) -> None:
    # Implement handler logic
    # Use self._send(RpcResponse(...)) for success
    # Use self._send(GatewayUtils.make_error_response(...)) for errors
    await self._send(RpcResponse(id=request.id, result={"ok": True}))
```

### Step 3 — Verify auto-discovery

No manual registration is needed. `GatewayUtils.REQUEST_TYPES` auto-discovers all `GatewayRequest` subclasses in the `Requests` namespace via `inspect.getmembers`. The `SessionService._build_dispatch_table()` scans for `_gateway_request_type` attributes at boot time.

---

## Key Patterns

### Auth Flow
The first message on any new WebSocket connection **must** be `method: "auth"` with a `token` param matching the token written to disk. `GatewayService._handle_new_connection` enforces this before handing off to `SessionService`.

### Dispatch Mechanism
1. `SessionService._dispatch` parses raw JSON into `RpcRequest`
2. `GatewayUtils.parse_request` maps the method name to a typed `GatewayRequest` subclass
3. `SessionService._handlers` (built by `_build_dispatch_table`) routes by request type to the `@on`-decorated method

### The `@on` Decorator
- Non-wrapping: sets `method._gateway_request_type = request_type` and returns the method unaltered
- Used exclusively in `SessionService` for dispatch registration
- Must not be used outside the gateway domain

### Streaming Notifications
- Outbound-only, no request id — uses `RpcNotification`
- Sent via `SessionService.notify(method, params)`
- Triggered by `GatewayService.post_message` which creates `asyncio` tasks for each notification

### Error Responses
Use `GatewayUtils.make_error_response(id, code, message)` with the predefined error constants from `protocol.py`:
- `ERR_PARSE` (-32700)
- `ERR_INVALID_REQUEST` (-32600)
- `ERR_METHOD_NOT_FOUND` (-32601)
- `ERR_UNAUTHORIZED` (-32000)
- `ERR_INTERNAL` (-32001)
