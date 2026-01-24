""""""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.config.byte_config import ByteConfig
    from byte.config.exceptions import ByteConfigException
    from byte.config.migrator import Migrator
    from byte.config.repository import Repository

__all__ = (
    "ByteConfig",
    "ByteConfigException",
    "Migrator",
    "Repository",
)

_dynamic_imports = {
    # keep-sorted start
    "ByteConfig": "byte_config",
    "ByteConfigException": "exceptions",
    "Migrator": "migrator",
    "Repository": "repository",
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
