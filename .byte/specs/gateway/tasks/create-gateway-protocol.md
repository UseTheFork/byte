---
files:
  create:
  - src/byte/gateway/protocol.py
  edit: []
  reference: []
id: create-gateway-protocol
notes: []
order: 3
status: completed
---
# Gateway Domain — `protocol.py`

**Goal:** Define all JSON-RPC 2.0 message envelope models and error constants used by every other file in the gateway domain.
**Architecture:** Pure Pydantic models with `extra="forbid"`. All envelope construction goes here — no other file may build raw RPC dicts. A single `make_error_response` helper keeps error construction DRY.

---

Create `src/byte/gateway/protocol.py` with the following content:

## Error code constants

```python
ERR_PARSE: int = -32700
ERR_INVALID_REQUEST: int = -32600
ERR_METHOD_NOT_FOUND: int = -32601
ERR_UNAUTHORIZED: int = -32000
ERR_INTERNAL: int = -32001
```

## Models

All models must set `model_config = ConfigDict(extra="forbid")`.

```python
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict


class RpcError(BaseModel):
    """JSON-RPC 2.0 error object."""
    model_config = ConfigDict(extra="forbid")

    code: int
    message: str
    data: Any | None = None  # Any is permitted: JSON-RPC spec allows arbitrary error data


class RpcRequest(BaseModel):
    """Inbound JSON-RPC 2.0 request from an external client."""
    model_config = ConfigDict(extra="forbid")

    jsonrpc: Literal["2.0"]
    id: str | int
    method: str
    params: dict[str, Any] | None = None


class RpcResponse(BaseModel):
    """Final result envelope for a JSON-RPC 2.0 request id."""
    model_config = ConfigDict(extra="forbid")

    jsonrpc: Literal["2.0"] = "2.0"
    id: str | int
    result: dict[str, Any] | None = None
    error: RpcError | None = None


class RpcNotification(BaseModel):
    """Streaming event pushed to the client with no request id."""
    model_config = ConfigDict(extra="forbid")

    jsonrpc: Literal["2.0"] = "2.0"
    method: str
    params: dict[str, Any]
```

## Helper

```python
def make_error_response(id: str | int | None, code: int, message: str) -> RpcResponse:
    """Build an RpcResponse carrying an RpcError for the given code and message."""
    return RpcResponse(
        id=id if id is not None else 0,
        error=RpcError(code=code, message=message),
    )
```

> `id=0` is the conventional fallback when the request id cannot be parsed (e.g. on `ERR_PARSE`). This keeps the return type as `RpcResponse` without introducing `Optional`.
