"""Mixins."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.support.mixins.bootable import Bootable
    from byte.support.mixins.conditionable import Conditionable
    from byte.support.mixins.configurable import Configurable
    from byte.support.mixins.eventable import Eventable
    from byte.support.mixins.injectable import Injectable
    from byte.support.mixins.user_interactive import UserInteractive

__all__ = (
    "Bootable",
    "Conditionable",
    "Configurable",
    "Eventable",
    "Injectable",
    "UserInteractive",
)

_dynamic_imports = {
    "Bootable": "bootable",
    "Conditionable": "conditionable",
    "Configurable": "configurable",
    "Eventable": "eventable",
    "Injectable": "injectable",
    "UserInteractive": "user_interactive",
}


def __getattr__(attr_name: str) -> object:
    module_name = _dynamic_imports.get(attr_name)
    parent = __spec__.parent if __spec__ is not None else None
    result = import_attr(attr_name, module_name, parent)
    globals()[attr_name] = result
    return result


def __dir__() -> list[str]:
    return list(__all__)
