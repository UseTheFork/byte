"""System domain for core system commands and configuration management."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.system.command.exit_command import ExitCommand
    from byte.system.config import PathsConfig, SystemConfig
    from byte.system.service.config_loader_service import ConfigLoaderService
    from byte.system.service.config_writer_service import ConfigWriterService
    from byte.system.service.system_context_service import SystemContextService
    from byte.system.service_provider import SystemServiceProvider

__all__ = (
    "ConfigLoaderService",
    "ConfigWriterService",
    "ExitCommand",
    "PathsConfig",
    "SystemConfig",
    "SystemContextService",
    "SystemServiceProvider",
)

_dynamic_imports = {
    # keep-sorted start
    "ConfigLoaderService": "service.config_loader_service",
    "ConfigWriterService": "service.config_writer_service",
    "ExitCommand": "command.exit_command",
    "PathsConfig": "config",
    "SystemConfig": "config",
    "SystemContextService": "service.system_context_service",
    "SystemServiceProvider": "service_provider",
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
