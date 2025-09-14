# In container.py or a new context.py file
from contextvars import ContextVar
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from byte.container import Container

container_context: ContextVar[Optional["Container"]] = ContextVar(
    "container", default=None
)


def get_container() -> "Container":
    """Get the current container from context."""
    container = container_context.get()
    if container is None:
        raise RuntimeError("No container available in current context")
    return container
