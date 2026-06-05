from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

# Error code constants
ERR_PARSE: int = -32700
ERR_INVALID_REQUEST: int = -32600
ERR_METHOD_NOT_FOUND: int = -32601
ERR_UNAUTHORIZED: int = -32000
ERR_INTERNAL: int = -32001


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


def make_error_response(id: str | int | None, code: int, message: str) -> RpcResponse:
    """Build an RpcResponse carrying an RpcError for the given code and message."""
    return RpcResponse(
        id=id if id is not None else 0,
        error=RpcError(code=code, message=message),
    )
