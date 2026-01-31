""""""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.clipboard.command.copy_command import CopyCommand
    from byte.clipboard.service.clipboard_service import ClipboardService
    from byte.clipboard.service_provider import ClipboardServiceProvider

__all__ = (
    "ClipboardService",
    "ClipboardServiceProvider",
    "CopyCommand",
)

_dynamic_imports = {
    # keep-sorted start
    "ClipboardService": "service.clipboard_service",
    "ClipboardServiceProvider": "service_provider",
    "CopyCommand": "command.copy_command",
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
