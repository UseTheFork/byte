""""""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.foundation.bootstrap.boot_providers import BootProviders
    from byte.foundation.bootstrap.handle_exceptions import HandleExceptions
    from byte.foundation.bootstrap.load_configuration import LoadConfiguration
    from byte.foundation.bootstrap.register_providers import RegisterProviders

__all__ = (
    "BootProviders",
    "HandleExceptions",
    "LoadConfiguration",
    "RegisterProviders",
)

_dynamic_imports = {
    # keep-sorted start
    "BootProviders": "boot_providers",
    "HandleExceptions": "handle_exceptions",
    "LoadConfiguration": "load_configuration",
    "RegisterProviders": "register_providers",
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
