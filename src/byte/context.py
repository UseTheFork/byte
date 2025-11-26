from contextvars import ContextVar
from typing import Optional, Type, TypeVar

from byte.container import Container

T = TypeVar("T")

container_context: ContextVar[Optional["Container"]] = ContextVar("container", default=None)


def get_container() -> "Container":
    """Get the current container from context."""
    container = container_context.get()
    if container is None:
        raise RuntimeError("No container available in current context")
    return container


async def make[T](service_class: Type[T]) -> T:
    """Convenience method to get a service from the current container context."""
    container = get_container()
    return await container.make(service_class)
