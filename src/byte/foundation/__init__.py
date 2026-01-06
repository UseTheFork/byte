""""""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.foundation.application import Application
    from byte.foundation.console.console import Console
    from byte.foundation.console.kernel import Kernel
    from byte.foundation.container import Container
    from byte.foundation.event_bus import EventBus, EventType, Payload
    from byte.foundation.task_manager import TaskManager

__all__ = (
    "Application",
    "Console",
    "Container",
    "EventBus",
    "EventType",
    "Kernel",
    "Payload",
    "TaskManager",
)

_dynamic_imports = {
    # keep-sorted start
    "Application": "application",
    "Console": "console.console",
    "Container": "container",
    "EventBus": "event_bus",
    "EventType": "event_bus",
    "Kernel": "console.kernel",
    "Payload": "event_bus",
    "TaskManager": "task_manager",
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
