from enum import Enum

from pydantic.dataclasses import dataclass


class BlockType(Enum):
    """Type of edit block operation."""

    EDIT = "edit"  # Modify existing file content
    ADD = "add"  # Create new file
    REMOVE = "remove"  # Remove existing file


class BlockStatus(Enum):
    """Status of edit block validation."""

    VALID = "valid"
    READ_ONLY_ERROR = "read_only_error"
    SEARCH_NOT_FOUND_ERROR = "search_not_found_error"
    FILE_OUTSIDE_PROJECT_ERROR = "file_outside_project_error"


@dataclass
class EditFormatPrompts:
    """"""

    system: str
    examples: list[tuple[str, str]]


@dataclass
class ShellCommandBlock:
    """Represents a single shell command operation to be executed.

    Usage: `block = ShellCommandBlock(command="pytest tests/", working_dir="/project")`
    """

    command: str
    working_dir: str = ""
    block_status: BlockStatus = BlockStatus.VALID
    status_message: str = ""


@dataclass
class SearchReplaceBlock:
    """Represents a single edit operation with file path, search content, and replacement content."""

    operation: str
    file_path: str
    search_content: str
    replace_content: str
    block_type: BlockType = BlockType.EDIT
    block_status: BlockStatus = BlockStatus.VALID
    status_message: str = ""

    def to_search_replace_format(
        self,
        fence: str = "```",
        operation: str = "+++++++",
        search: str = "<<<<<<< SEARCH",
        divider: str = "=======",
        replace: str = ">>>>>>> REPLACE",
    ) -> str:
        """Convert SearchReplaceBlock back to search/replace block format.

        Generates the formatted search/replace block string that can be used
        for display, logging, or re-processing through the edit format system.

        Returns:
            str: Formatted search/replace block string

        Usage: `formatted = block.to_search_replace_format()` -> formatted block string
        """
        return f"""{fence}
{operation} {self.file_path}
{search}
{self.search_content}
{divider}
{self.replace_content}
{replace}
{fence}"""
