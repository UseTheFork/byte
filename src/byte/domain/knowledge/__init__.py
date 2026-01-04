"""Knowledge domain commands for context management."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.domain.knowledge.command.context_add_file_command import ContextAddFileCommand
    from byte.domain.knowledge.command.context_drop_command import ContextDropCommand
    from byte.domain.knowledge.command.context_list_command import ContextListCommand
    from byte.domain.knowledge.command.web_command import WebCommand
    from byte.domain.knowledge.models import SessionContextModel
    from byte.domain.knowledge.service.cli_context_display_service import CLIContextDisplayService
    from byte.domain.knowledge.service.convention_context_service import ConventionContextService
    from byte.domain.knowledge.service.session_context_service import SessionContextService
    from byte.domain.knowledge.service_provider import KnowledgeServiceProvider

__all__ = (
    "CLIContextDisplayService",
    "ContextAddFileCommand",
    "ContextDropCommand",
    "ContextListCommand",
    "ConventionContextService",
    "KnowledgeServiceProvider",
    "SessionContextModel",
    "SessionContextService",
    "WebCommand",
)

_dynamic_imports = {
    # keep-sorted start
    "CLIContextDisplayService": "service.cli_context_display_service",
    "ContextAddFileCommand": "command.context_add_file_command",
    "ContextDropCommand": "command.context_drop_command",
    "ContextListCommand": "command.context_list_command",
    "ConventionContextService": "service.convention_context_service",
    "KnowledgeServiceProvider": "service_provider",
    "SessionContextModel": "models",
    "SessionContextService": "service.session_context_service",
    "WebCommand": "command.web_command",
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
