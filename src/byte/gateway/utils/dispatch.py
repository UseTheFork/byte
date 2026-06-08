"""Decorator-based dispatch system for gateway requests."""

from typing import Callable, TypeVar

from byte.gateway.requests import GatewayRequest

DecoratedType = TypeVar("DecoratedType")


def on(request_type: type[GatewayRequest]) -> Callable[[DecoratedType], DecoratedType]:
    """Decorator to declare that the method is a handler for a specific gateway request type.

    The decorator tags the method with a `_gateway_request_type` attribute without wrapping.

    Example:
        ```python
        @on(Requests.Execute)
        def handle_execute(self, request: Requests.Execute) -> None:
            ...
        ```

    Args:
        request_type: The gateway request type (i.e. a GatewayRequest subclass).
    """

    def decorator(method: DecoratedType) -> DecoratedType:
        """Store request type in method attribute, return callable unaltered."""
        setattr(method, "_gateway_request_type", request_type)
        return method

    return decorator
