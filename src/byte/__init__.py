"""Byte - AI-powered coding assistant."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.command import ByteArgumentParser, Command, CommandRegistryService
    from byte.event import Event, EventBus
    from byte.foundation import Application, TaskManager
    from byte.logging import LogService
    from byte.support import Service, ServiceProvider
    from byte.support.utils import dd, dump

__all__ = (
    "Application",
    "ByteArgumentParser",
    "Command",
    "CommandRegistryService",
    "Event",
    "EventBus",
    "Log",
    "LogService",
    "Service",
    "ServiceProvider",
    "TaskManager",
    "dd",
    "dump",
)

_dynamic_imports = {
    # keep-sorted start
    "Application": "foundation",
    "ByteArgumentParser": "command",
    "Command": "command",
    "CommandRegistryService": "command",
    "Console": "foundation",
    "Event": "event",
    "EventBus": "event",
    "LogService": "logging",
    "Service": "support",
    "ServiceProvider": "support",
    "TaskManager": "foundation",
    "dd": "support.utils",
    "dump": "support.utils",
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
