"""Unit tests for GatewayUtils."""

import pytest

from byte.gateway.protocol import (
    ERR_INTERNAL,
    RpcError,
    RpcRequest,
    RpcResponse,
)
from byte.gateway.requests import GatewayRequest, Requests
from byte.gateway.utils import GatewayUtils


def test_request_types_contains_configure() -> None:
    """REQUEST_TYPES contains 'configure' key for Requests.Configure."""
    assert "configure" in GatewayUtils.REQUEST_TYPES
    assert GatewayUtils.REQUEST_TYPES["configure"] is Requests.Configure


def test_request_types_contains_add_file() -> None:
    """REQUEST_TYPES contains 'add_file' key for Requests.AddFile."""
    assert "add_file" in GatewayUtils.REQUEST_TYPES
    assert GatewayUtils.REQUEST_TYPES["add_file"] is Requests.AddFile


def test_request_types_contains_drop_file() -> None:
    """REQUEST_TYPES contains 'drop_file' key for Requests.DropFile."""
    assert "drop_file" in GatewayUtils.REQUEST_TYPES
    assert GatewayUtils.REQUEST_TYPES["drop_file"] is Requests.DropFile


def test_request_types_contains_context_add_file() -> None:
    """REQUEST_TYPES contains 'context_add_file' key for Requests.ContextAddFile."""
    assert "context_add_file" in GatewayUtils.REQUEST_TYPES
    assert GatewayUtils.REQUEST_TYPES["context_add_file"] is Requests.ContextAddFile


def test_request_types_all_are_request_subclasses() -> None:
    """All REQUEST_TYPES values are GatewayRequest subclasses."""
    for request_class in GatewayUtils.REQUEST_TYPES.values():
        assert issubclass(request_class, GatewayRequest)


def test_parse_configure_request() -> None:
    """parse_request converts RpcRequest to Requests.Configure."""
    rpc = RpcRequest(
        jsonrpc="2.0",
        id=2,
        method="configure",
        params={"model": "gpt-4", "context_limit": 8192},
    )
    req = GatewayUtils.parse_request(rpc)

    assert isinstance(req, Requests.Configure)
    assert req.id == 2
    assert req.model == "gpt-4"
    assert req.context_limit == 8192


def test_parse_configure_with_partial_params() -> None:
    """parse_request handles partial params in Configure."""
    rpc = RpcRequest(jsonrpc="2.0", id="cfg-1", method="configure", params={"model": "gpt-3.5"})
    req = GatewayUtils.parse_request(rpc)

    assert isinstance(req, Requests.Configure)
    assert req.model == "gpt-3.5"
    assert req.context_limit is None


def test_parse_add_file_request() -> None:
    """parse_request converts RpcRequest to Requests.AddFile."""
    rpc = RpcRequest(
        jsonrpc="2.0",
        id=3,
        method="add_file",
        params={"file_path": "/path/to/file.py"},
    )
    req = GatewayUtils.parse_request(rpc)

    assert isinstance(req, Requests.AddFile)
    assert req.id == 3
    assert req.file_path == "/path/to/file.py"


def test_parse_drop_file_request() -> None:
    """parse_request converts RpcRequest to Requests.DropFile."""
    rpc = RpcRequest(
        jsonrpc="2.0",
        id="drop-1",
        method="drop_file",
        params={"file_path": "src/old.py"},
    )
    req = GatewayUtils.parse_request(rpc)

    assert isinstance(req, Requests.DropFile)
    assert req.id == "drop-1"
    assert req.file_path == "src/old.py"


def test_parse_context_add_file_request() -> None:
    """parse_request converts RpcRequest to Requests.ContextAddFile."""
    rpc = RpcRequest(
        jsonrpc="2.0",
        id="ctx-1",
        method="context_add_file",
        params={"file_path": "src/context.py"},
    )
    req = GatewayUtils.parse_request(rpc)

    assert isinstance(req, Requests.ContextAddFile)
    assert req.id == "ctx-1"
    assert req.file_path == "src/context.py"


def test_parse_request_with_none_params() -> None:
    """parse_request handles None params gracefully."""
    rpc = RpcRequest(jsonrpc="2.0", id=4, method="add_file", params=None)
    # This should raise because AddFile requires file_path field
    with pytest.raises(ValueError):  # noqa: PT011
        GatewayUtils.parse_request(rpc)


def test_parse_request_unknown_method() -> None:
    """parse_request raises ValueError for unknown method."""
    rpc = RpcRequest(jsonrpc="2.0", id="unknown-1", method="unknown_method", params={})
    with pytest.raises(ValueError, match="Unknown method"):
        GatewayUtils.parse_request(rpc)


def test_make_error_response_basic() -> None:
    """make_error_response returns proper RpcResponse with RpcError."""
    response = GatewayUtils.make_error_response("req-1", ERR_INTERNAL, "Something went wrong")

    assert isinstance(response, RpcResponse)
    assert response.id == "req-1"
    assert response.result is None
    assert response.error is not None
    assert isinstance(response.error, RpcError)
    assert response.error.code == ERR_INTERNAL
    assert response.error.message == "Something went wrong"


def test_make_error_response_numeric_id() -> None:
    """make_error_response handles numeric request id."""
    response = GatewayUtils.make_error_response(42, ERR_INTERNAL, "Error")

    assert response.id == 42
    assert response.error.code == ERR_INTERNAL


def test_make_error_response_none_id() -> None:
    """make_error_response defaults to 0 when id is None."""
    response = GatewayUtils.make_error_response(None, ERR_INTERNAL, "Parse error")

    assert response.id == 0
    assert response.error.message == "Parse error"


def test_make_error_response_jsonrpc_version() -> None:
    """make_error_response includes correct JSON-RPC version."""
    response = GatewayUtils.make_error_response("req-1", -32600, "Invalid Request")

    assert response.jsonrpc == "2.0"


def test_make_error_response_no_result() -> None:
    """make_error_response has no result field."""
    response = GatewayUtils.make_error_response("req-1", -32601, "Method not found")

    assert response.result is None
