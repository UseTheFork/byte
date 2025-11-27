from enum import Enum

from pydantic.dataclasses import dataclass

from byte.core.utils import list_to_multiline_text


class BoundaryType(str, Enum):
    """Type of boundary marker for content sections."""

    ROLE = "role"
    TASK = "task"
    RULES = "rules"
    GOAL = "goal"
    RESPONSE_FORMAT = "response_format"

    ERROR = "error"

    CONVENTION = "convention"
    SESSION_CONTEXT = "session_context"
    SHELL_COMMAND = "shell_command"
    FILE = "file"
    SEARCH = "search"
    REPLACE = "replace"
    EXAMPLE = "example"
    REINFORCEMENT = "reinforcement"
    PROJECT_HIERARCHY = "project_hierarchy"
    CONSTRAINTS = "constraints"

    CRITICAL_REQUIREMENTS = "response_requirements"
    RECOVERY_STEPS = "recovery_steps"

    CONTEXT = "context"

    SYSTEM_CONTEXT = "system_context"


class BlockType(Enum):
    """Type of edit block operation."""

    EDIT = "edit"  # Modify existing file content
    ADD = "add"  # Create new file
    REMOVE = "remove"  # Remove existing file
    REPLACE = "replace"


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
    enforcement: str
    recovery_steps: str
    examples: list[tuple[str, str]]

    # shell_system: str
    # shell_examples: list[tuple[str, str]]


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

    file_path: str
    search_content: str
    replace_content: str
    block_type: BlockType = BlockType.EDIT
    block_status: BlockStatus = BlockStatus.VALID
    status_message: str = ""

    def to_search_replace_format(self) -> str:
        """Convert SearchReplaceBlock back to search/replace block format.

        Generates the formatted search/replace block string that can be used
        for display, logging, or re-processing through the edit format system.

        Returns:
                str: Formatted search/replace block string

        Usage: `formatted = block.to_search_replace_format()` -> formatted block string
        """
        from byte.domain.prompt_format.utils.boundary import Boundary

        sections = [
            Boundary.open(BoundaryType.ERROR, meta={"operation": self.block_type.value}),
            f"**File:** `{self.file_path}`",
            "",
        ]
        # Add status information if there's an error
        if self.block_status != BlockStatus.VALID:
            sections.extend(
                [
                    f"**Status:** {self.block_status.value}",
                    f"**Issue:** {self.status_message}",
                    "",
                ]
            )

        sections.extend(
            [
                Boundary.open(BoundaryType.SEARCH),
                self.search_content,
                Boundary.close(BoundaryType.SEARCH),
                "",
                Boundary.open(BoundaryType.REPLACE),
                self.replace_content,
                Boundary.close(BoundaryType.REPLACE),
                "",
                Boundary.close(BoundaryType.ERROR),
            ]
        )

        return list_to_multiline_text(sections)
