"""L"""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.logging.service.log_service import LogService
    from byte.logging.service_provider import LogServiceProvider

__all__ = (
    "LogService",
    "LogServiceProvider",
)

_dynamic_imports = {
    "LogService": "service.log_service",
    "LogServiceProvider": "service_provider",
}


def __getattr__(attr_name: str) -> object:
    module_name = _dynamic_imports.get(attr_name)
    parent = __spec__.parent if __spec__ is not None else None
    result = import_attr(attr_name, module_name, parent)
    globals()[attr_name] = result
    return result


def __dir__() -> list[str]:
    return list(__all__)
