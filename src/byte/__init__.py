"""Byte - AI-powered coding assistant."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.container import Container
    from byte.context import make
    from byte.core.logging import log
    from byte.core.service.base_service import Service
    from byte.core.service_provider import ServiceProvider
    from byte.core.utils.dump import dd, dump

__version__ = "0.7.1"

__all__ = (
    "Container",
    "Service",
    "ServiceProvider",
    "dd",
    "dump",
    "log",
    "make",
)

_dynamic_imports = {
    # keep-sorted start
    "Container": "container",
    "Service": "core",
    "ServiceProvider": "core",
    "dd": "core",
    "dump": "core",
    "log": "core",
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
