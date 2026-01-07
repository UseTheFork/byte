"""Byte - AI-powered coding assistant."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.cli import Command
    from byte.context import make
    from byte.foundation import Application, Console, EventBus, EventType, Payload, TaskManager
    from byte.support import Service, ServiceProvider
    from byte.support.utils import dd, dump

__version__ = "0.7.1"

__all__ = (
    "Application",
    "Command",
    "Console",
    "EventBus",
    "EventType",
    "Payload",
    "Service",
    "ServiceProvider",
    "TaskManager",
    "dd",
    "dump",
    "make",
)

_dynamic_imports = {
    # keep-sorted start
    "Application": "foundation",
    "Command": "cli",
    "Console": "foundation",
    "EventBus": "foundation",
    "EventType": "foundation",
    "Payload": "foundation",
    "Service": "support",
    "ServiceProvider": "support",
    "TaskManager": "foundation",
    "dd": "support.utils",
    "dump": "support.utils",
    "make": "context",
    # keep-sorted end
}


def __getattr__(attr_name: str) -> object:
    module_name = _dynamic_imports.get(attr_name)
    parent = __spec__.parent if __spec__ is not None else None
    result = import_attr(attr_name, module_name, parent)
    globals()[attr_name] = result
    return result


def __dir__() -> list[str]:
    return list(__all__)
