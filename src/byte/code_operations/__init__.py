"""Prompt format domain for edit block parsing and shell command execution."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.code_operations.blocks.base import BaseBlock
    from byte.code_operations.blocks.base_operation_block import BaseOperationBlock
    from byte.code_operations.blocks.file.base_file_operation_block import BaseFileOperationBlock
    from byte.code_operations.blocks.raw import RawBlock
    from byte.code_operations.constants import EDIT_BLOCK_NAME
    from byte.code_operations.exceptions import NoBlocksFoundError, PreFlightCheckError, PreFlightUnparsableError
    from byte.code_operations.prompts import edit_block_enforcement, edit_block_messages
    from byte.code_operations.schemas import (
        BlockStatus,
        BlockType,
        EditFormatPrompts,
        ShellCommandBlock,
    )
    from byte.code_operations.service.edit_block_service import EditBlockService
    from byte.code_operations.service.raw_block_service import RawBlockService
    from byte.code_operations.service.shell_command_service import ShellCommandService
    from byte.code_operations.service_provider import PromptFormatProvider

__all__ = (
    "EDIT_BLOCK_NAME",
    "BaseBlock",
    "BaseFileOperationBlock",
    "BaseOperationBlock",
    "BlockStatus",
    "BlockType",
    "EditBlockService",
    "EditFormatConfig",
    "EditFormatError",
    "EditFormatPrompts",
    "EditFormatService",
    "FileOutsideProjectError",
    "NoBlocksFoundError",
    "PreFlightCheckError",
    "PreFlightUnparsableError",
    "PromptFormatProvider",
    "RawBlock",
    "RawBlockService",
    "ReadOnlyFileError",
    "SearchContentNotFoundError",
    "ShellCommandBlock",
    "ShellCommandService",
    "edit_block_enforcement",
    "edit_block_messages",
)


_dynamic_imports = {
    # keep-sorted start
    "BaseBlock": "blocks.base",
    "BaseFileOperationBlock": "blocks.file.base_file_operation_block",
    "BaseOperationBlock": "blocks.base_operation_block",
    "BlockStatus": "schemas",
    "BlockType": "schemas",
    "EDIT_BLOCK_NAME": "constants",
    "EditBlockService": "service.edit_block_service",
    "EditFormatConfig": "config",
    "EditFormatError": "exceptions",
    "EditFormatPrompts": "schemas",
    "EditFormatService": "service.edit_format_service",
    "FileOutsideProjectError": "exceptions",
    "NoBlocksFoundError": "exceptions",
    "PreFlightCheckError": "exceptions",
    "PreFlightUnparsableError": "exceptions",
    "PromptFormatProvider": "service_provider",
    "RawBlock": "blocks.raw",
    "RawBlockService": "service.raw_block_service",
    "ReadOnlyFileError": "exceptions",
    "SearchContentNotFoundError": "exceptions",
    "ShellCommandBlock": "schemas",
    "ShellCommandService": "service.shell_command_service",
    "edit_block_enforcement": "prompts",
    "edit_block_messages": "prompts",
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
