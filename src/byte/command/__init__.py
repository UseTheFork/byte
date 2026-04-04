"""CLI domain for terminal interface and user interactions."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.command.argparse.base import ByteArgumentParser
    from byte.command.command import Command
    from byte.command.service.command_registry_service import CommandRegistryService
    from byte.command.service_provider import CommandServiceProvider

__all__ = (
    "ByteArgumentParser",
    "Command",
    "CommandRegistryService",
    "CommandServiceProvider",
)

_dynamic_imports = {
    # keep-sorted start
    "ByteArgumentParser": "argparse.base",
    "Command": "command",
    "CommandRegistryService": "service.command_registry_service",
    "CommandServiceProvider": "service_provider",
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
