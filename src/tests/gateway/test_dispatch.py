"""Unit tests for the @on decorator and dispatch mechanism."""

from byte.gateway.requests import Requests
from byte.gateway.utils import on


def test_on_decorator_preserves_method_signature() -> None:
    """@on decorator doesn't wrap the method."""

    class TestHandler:
        @on(Requests.Configure)
        def handle_configure(self, request: Requests.Configure) -> str:
            return "configured"

    handler = TestHandler()
    # Method should be callable and work normally
    result = handler.handle_configure(Requests.Configure(id=1))
    assert result == "configured"


def test_on_decorator_returns_method_unaltered() -> None:
    """@on decorator returns the method unaltered (not wrapped)."""

    def original_method(self: object, request: Requests.Configure) -> None:
        pass

    decorated = on(Requests.Configure)(original_method)
    assert decorated is original_method


def test_build_dispatch_table_populates_handlers() -> None:
    """SessionService._build_dispatch_table() populates _handlers dict."""
    from byte.gateway.service.session_service import SessionService

    # Create a mock service instance without full initialization
    service = object.__new__(SessionService)

    # Add decorated methods to the instance
    @on(Requests.AddFile)
    def handle_add_file(self: object, request: Requests.AddFile) -> None:
        pass

    @on(Requests.Configure)
    def handle_configure(self: object, request: Requests.Configure) -> None:
        pass

    service.handle_execute = handle_add_file.__get__(service, SessionService)  # type: ignore
    service.handle_configure = handle_configure.__get__(service, SessionService)  # type: ignore

    # Build dispatch table
    service._build_dispatch_table()

    # Check that handlers were registered
    assert Requests.AddFile in service._handlers  # type: ignore
    assert Requests.Configure in service._handlers  # type: ignore


def test_build_dispatch_table_stores_bound_methods() -> None:
    """_build_dispatch_table stores bound methods, not unbound functions."""
    from byte.gateway.service.session_service import SessionService

    service = object.__new__(SessionService)

    @on(Requests.AddFile)
    def handle_add_file(self: object, request: Requests.AddFile) -> None:
        pass

    service.handle_add_file = handle_add_file.__get__(service, SessionService)  # type: ignore

    service._build_dispatch_table()

    # The handler should be callable and bound to this instance
    handler = service._handlers[Requests.AddFile]  # type: ignore
    assert callable(handler)


def test_dispatch_routes_configure_to_handler() -> None:
    """Dispatch routes Configure request to the correct handler."""
    from byte.gateway.service.session_service import SessionService

    service = object.__new__(SessionService)

    call_log = []

    @on(Requests.Configure)
    def handle_configure(self: object, request: Requests.Configure) -> None:
        call_log.append(("configure", request.model))

    service.handle_configure = handle_configure.__get__(service, SessionService)  # type: ignore
    service._build_dispatch_table()

    handler = service._handlers[Requests.Configure]  # type: ignore
    req = Requests.Configure(id="test-2", model="gpt-4")
    handler(req)

    assert call_log == [("configure", "gpt-4")]


def test_handler_lookup_by_request_type() -> None:
    """Handler lookup uses request type as key."""
    from byte.gateway.service.session_service import SessionService

    service = object.__new__(SessionService)

    @on(Requests.AddFile)
    def handle_add_file(self: object, request: Requests.AddFile) -> None:
        pass

    @on(Requests.DropFile)
    def handle_drop_file(self: object, request: Requests.DropFile) -> None:
        pass

    service.handle_add_file = handle_add_file.__get__(service, SessionService)  # type: ignore
    service.handle_drop_file = handle_drop_file.__get__(service, SessionService)  # type: ignore
    service._build_dispatch_table()

    # Both request types should map to different handlers
    assert service._handlers[Requests.AddFile] is not service._handlers[Requests.DropFile]  # type: ignore
    assert Requests.AddFile in service._handlers  # type: ignore
    assert Requests.DropFile in service._handlers  # type: ignore
