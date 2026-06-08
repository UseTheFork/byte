"""Unit tests for gateway Request dataclasses."""

from byte.gateway.requests import GatewayRequest, Requests


def test_gateway_request_has_id_field() -> None:
    """GatewayRequest base class carries the id field."""

    class TestRequest(GatewayRequest):
        pass

    req = TestRequest(id=42)
    assert req.id == 42


def test_configure_instantiation() -> None:
    """Configure request can be instantiated with id and optional fields."""
    req = Requests.Configure(id="req-1", model="gpt-4", context_limit=8192)
    assert req.id == "req-1"
    assert req.model == "gpt-4"
    assert req.context_limit == 8192


def test_configure_with_defaults() -> None:
    """Configure request optional fields default to None."""
    req = Requests.Configure(id=2)
    assert req.id == 2
    assert req.model is None
    assert req.context_limit is None


def test_configure_partial_fields() -> None:
    """Configure request can set only model without context_limit."""
    req = Requests.Configure(id="req-2", model="gpt-3.5")
    assert req.model == "gpt-3.5"
    assert req.context_limit is None


def test_add_file_instantiation() -> None:
    """AddFile request can be instantiated with id and file_path."""
    req = Requests.AddFile(id="req-1", file_path="/path/to/file.py")
    assert req.id == "req-1"
    assert req.file_path == "/path/to/file.py"


def test_add_file_with_numeric_id() -> None:
    """AddFile request supports numeric id."""
    req = Requests.AddFile(id=4, file_path="src/main.py")
    assert req.id == 4
    assert req.file_path == "src/main.py"


def test_drop_file_instantiation() -> None:
    """DropFile request can be instantiated with id and file_path."""
    req = Requests.DropFile(id="req-1", file_path="/path/to/file.py")
    assert req.id == "req-1"
    assert req.file_path == "/path/to/file.py"


def test_drop_file_with_numeric_id() -> None:
    """DropFile request supports numeric id."""
    req = Requests.DropFile(id=5, file_path="src/old.py")
    assert req.id == 5
    assert req.file_path == "src/old.py"


def test_context_add_file_instantiation() -> None:
    """ContextAddFile request can be instantiated with id and file_path."""
    req = Requests.ContextAddFile(id="req-1", file_path="/path/to/file.py")
    assert req.id == "req-1"
    assert req.file_path == "/path/to/file.py"


def test_context_add_file_with_numeric_id() -> None:
    """ContextAddFile request supports numeric id."""
    req = Requests.ContextAddFile(id=6, file_path="src/context.py")
    assert req.id == 6
    assert req.file_path == "src/context.py"


def test_context_drop_file_instantiation() -> None:
    """ContextDropFile request can be instantiated with id and file_path."""
    req = Requests.ContextDropFile(id="req-1", file_path="/path/to/file.py")
    assert req.id == "req-1"
    assert req.file_path == "/path/to/file.py"


def test_context_drop_file_with_numeric_id() -> None:
    """ContextDropFile request supports numeric id."""
    req = Requests.ContextDropFile(id=7, file_path="src/context.py")
    assert req.id == 7
    assert req.file_path == "src/context.py"
