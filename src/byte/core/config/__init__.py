"""Mixins."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.core.mixins.bootable import Bootable
    from byte.core.mixins.conditionable import Conditionable
    from byte.core.mixins.configurable import Configurable
    from byte.core.mixins.eventable import Eventable
    from byte.core.mixins.injectable import Injectable
    from byte.core.mixins.user_interactive import UserInteractive

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
    result = import_attr(attr_name, module_name, __spec__.parent)  # ty:ignore[possibly-missing-attribute]
    globals()[attr_name] = result
    return result


def __dir__() -> list[str]:
    return list(__all__)
