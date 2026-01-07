from contextvars import ContextVar
from typing import Optional, Type, TypeVar

from byte import Application, Log

T = TypeVar("T")

application_context: ContextVar[Optional["Application"]] = ContextVar("application", default=None)


def get_application() -> Application:
    """Get the current container from context."""
    container = application_context.get()
    if container is None:
        raise RuntimeError("No container available in current context")
    return container


def make[T](service_class: Type[T]) -> T:
    """Convenience method to get a service from the current container context."""
    app = get_application()
    return app.make(service_class)


def log() -> Log:
    """"""
    app = get_application()
    return app.make(Log)
