"""Memory domain for conversation history and thread management."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.memory.command.clear_command import ClearCommand
    from byte.memory.command.reset_command import ResetCommand
    from byte.memory.command.show_command import ShowCommand
    from byte.memory.command.undo_command import UndoCommand
    from byte.memory.service.memory_service import MemoryService
    from byte.memory.service_provider import MemoryServiceProvider

__all__ = (
    "ClearCommand",
    "MemoryService",
    "MemoryServiceProvider",
    "ResetCommand",
    "ShowCommand",
    "UndoCommand",
)

_dynamic_imports = {
    # keep-sorted start
    "ClearCommand": "command.clear_command",
    "MemoryService": "service.memory_service",
    "MemoryServiceProvider": "service_provider",
    "ResetCommand": "command.reset_command",
    "ShowCommand": "command.show_command",
    "UndoCommand": "command.undo_command",
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
