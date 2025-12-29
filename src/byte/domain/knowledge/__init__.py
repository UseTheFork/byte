"""Knowledge domain commands for context management."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.domain.knowledge.command.context_add_file_command import ContextAddFileCommand
    from byte.domain.knowledge.command.context_drop_command import ContextDropCommand
    from byte.domain.knowledge.command.context_list_command import ContextListCommand
    from byte.domain.knowledge.command.web_command import WebCommand

__all__ = (
    "ContextAddFileCommand",
    "ContextDropCommand",
    "ContextListCommand",
    "WebCommand",
)

_dynamic_imports = {
    # keep-sorted start
    "ContextAddFileCommand": "context_add_file_command",
    "ContextDropCommand": "context_drop_command",
    "ContextListCommand": "context_list_command",
    "WebCommand": "web_command",
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
