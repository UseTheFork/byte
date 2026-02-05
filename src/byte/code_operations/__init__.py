"""Prompt format domain for edit block parsing and shell command execution."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.code_operations.schemas import (
        BlockStatus,
        BlockType,
        BoundaryType,
        EditFormatPrompts,
        RawSearchReplaceBlock,
        SearchReplaceBlock,
        ShellCommandBlock,
    )
    from byte.code_operations.service.edit_format_service import EditFormatService
    from byte.code_operations.service.parser_service import ParserService
    from byte.code_operations.service.shell_command_service import ShellCommandService
    from byte.code_operations.service_provider import PromptFormatProvider
    from byte.code_operations.utils.boundary import Boundary

__all__ = (
    "EDIT_BLOCK_NAME",
    "BlockStatus",
    "BlockType",
    "Boundary",
    "BoundaryType",
    "EditFormatConfig",
    "EditFormatError",
    "EditFormatPrompts",
    "EditFormatService",
    "FileOutsideProjectError",
    "NoBlocksFoundError",
    "ParserService",
    "PreFlightCheckError",
    "PreFlightUnparsableError",
    "PromptFormatProvider",
    "RawSearchReplaceBlock",
    "ReadOnlyFileError",
    "SearchContentNotFoundError",
    "SearchReplaceBlock",
    "ShellCommandBlock",
    "ShellCommandService",
)

_dynamic_imports = {
    # keep-sorted start
    "BlockStatus": "schemas",
    "BlockType": "schemas",
    "Boundary": "utils.boundary",
    "BoundaryType": "schemas",
    "EDIT_BLOCK_NAME": "constants",
    "EditFormatConfig": "config",
    "EditFormatError": "exceptions",
    "EditFormatPrompts": "schemas",
    "EditFormatService": "service.edit_format_service",
    "FileOutsideProjectError": "exceptions",
    "NoBlocksFoundError": "exceptions",
    "ParserService": "service.parser_service",
    "PreFlightCheckError": "exceptions",
    "PreFlightUnparsableError": "exceptions",
    "PromptFormatProvider": "service_provider",
    "RawSearchReplaceBlock": "schemas",
    "ReadOnlyFileError": "exceptions",
    "SearchContentNotFoundError": "exceptions",
    "SearchReplaceBlock": "schemas",
    "ShellCommandBlock": "schemas",
    "ShellCommandService": "service.shell_command_service",
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
