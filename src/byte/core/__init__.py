"""Core."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.core.array_store import ArrayStore
    from byte.core.config import BYTE_CACHE_DIR, BYTE_CONFIG_FILE, PROJECT_ROOT, ByteConfig, CLIArgs
    from byte.core.event_bus import EventBus, EventType, Payload
    from byte.core.exceptions import ByteConfigException
    from byte.core.logging import log
    from byte.core.service.base_service import Service
    from byte.core.service_provider import ServiceProvider
    from byte.core.task_manager import TaskManager
    from byte.core.utils.dump import dd, dump

__all__ = (
    "BYTE_CACHE_DIR",
    "BYTE_CONFIG_FILE",
    "PROJECT_ROOT",
    "ArrayStore",
    "ByteConfig",
    "ByteConfigException",
    "CLIArgs",
    "EventBus",
    "EventType",
    "Payload",
    "Service",
    "ServiceProvider",
    "TaskManager",
    "dd",
    "dump",
    "log",
)

_dynamic_imports = {
    # keep-sorted start
    "ArrayStore": "array_store",
    "BYTE_CACHE_DIR": "config",
    "BYTE_CONFIG_FILE": "config",
    "ByteConfig": "config",
    "ByteConfigException": "exceptions",
    "CLIArgs": "config",
    "EventBus": "event_bus",
    "EventType": "event_bus",
    "PROJECT_ROOT": "config",
    "Payload": "event_bus",
    "Service": "service.base_service",
    "ServiceProvider": "service_provider",
    "TaskManager": "task_manager",
    "dd": "utils.dump",
    "dump": "utils.dump",
    "log": "logging",
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
