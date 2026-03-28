from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.tui.byte_tui import ByteTUI
    from byte.tui.messages import Messages
    from byte.tui.service.tui_manager_service import TUIManagerService
    from byte.tui.service_provider import TUIServiceProvider


__all__ = ("ByteTUI", "Messages", "TUIManagerService", "TUIServiceProvider")

_dynamic_imports = {
    # keep-sorted start
    "ByteTUI": "byte_tui",
    "Messages": "messages",
    "TUIManagerService": "service.tui_manager_service",
    "TUIServiceProvider": "service_provider",
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
