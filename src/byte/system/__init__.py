"""System domain for core system commands and configuration management."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.system.command.exit_command import ExitCommand
    from byte.system.config import PathsConfig, SystemConfig
    from byte.system.events import SystemEvents
    from byte.system.service.config_writer_service import ConfigWriterService
    from byte.system.service.system_context_service import SystemContextService
    from byte.system.service_provider import SystemServiceProvider
    from byte.system.tools.user_confirm_or_input_tool import UserConfirmOrInputTool
    from byte.system.tools.user_confirm_tool import UserConfirmTool
    from byte.system.tools.user_input_text_tool import UserInputTextTool
    from byte.system.tools.user_select_tool import UserSelectTool

__all__ = (
    "ConfigWriterService",
    "ExitCommand",
    "PathsConfig",
    "SystemConfig",
    "SystemContextService",
    "SystemEvents",
    "SystemServiceProvider",
    "UserConfirmOrInputTool",
    "UserConfirmTool",
    "UserInputTextTool",
    "UserSelectTool",
)

_dynamic_imports = {
    # keep-sorted start
    "ConfigWriterService": "service.config_writer_service",
    "ExitCommand": "command.exit_command",
    "PathsConfig": "config",
    "SystemConfig": "config",
    "SystemContextService": "service.system_context_service",
    "SystemEvents": "events",
    "SystemServiceProvider": "service_provider",
    "UserConfirmOrInputTool": "tools.user_confirm_or_input_tool",
    "UserConfirmTool": "tools.user_confirm_tool",
    "UserInputTextTool": "tools.user_input_text_tool",
    "UserSelectTool": "tools.user_select_tool",
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
