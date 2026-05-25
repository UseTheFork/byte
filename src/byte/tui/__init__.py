from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.tui.byte_tui import ByteTUI
    from byte.tui.console import Console
    from byte.tui.events import TuiEvents
    from byte.tui.exceptions import InputCancelledError
    from byte.tui.messages import Messages, Status
    from byte.tui.schemas import AutocompleteOption
    from byte.tui.service.interactions_service import InteractionService
    from byte.tui.service.prompt_history_service import PromptHistoryService
    from byte.tui.service.tui_manager_service import TUIManagerService
    from byte.tui.service_provider import TUIServiceProvider


__all__ = (
    "AutocompleteOption",
    "ByteTUI",
    "Console",
    "InputCancelledError",
    "InteractionService",
    "Messages",
    "PromptHistoryService",
    "Status",
    "TUIManagerService",
    "TUIServiceProvider",
    "TuiEvents",
)

_dynamic_imports = {
    # keep-sorted start
    "AutocompleteOption": "schemas",
    "Console": "console",
    "ByteTUI": "byte_tui",
    "InputCancelledError": "exceptions",
    "InteractionService": "service.interactions_service",
    "Messages": "messages",
    "PromptHistoryService": "service.prompt_history_service",
    "Status": "messages",
    "TUIManagerService": "service.tui_manager_service",
    "TUIServiceProvider": "service_provider",
    "TuiEvents": "events",
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
