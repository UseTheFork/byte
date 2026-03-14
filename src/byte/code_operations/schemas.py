from enum import Enum
from typing import List

from pydantic.dataclasses import dataclass


class AICommentType(Enum):
    """Type of ai comment operation."""

    AI = "AI"

    def __str__(self):
        return self.value


class BlockType(str, Enum):
    """Type of edit block operation."""

    EDIT = "edit"  # Modify existing file content
    CREATE = "create"  # Create new file
    DELETE = "delete"  # Remove existing file
    REPLACE = "replace"
    UNKNOWN = "unknown"

    def __str__(self):
        return self.value


class BlockStatus(str, Enum):
    """Status of edit block validation."""

    UNKNOWN = "unknown"
    VALID = "valid"
    APPLIED = "applied"
    INVALID = "invalid"

    def __str__(self):
        return self.value


@dataclass
class EditFormatPrompts:
    """"""

    system: str
    enforcement: List[str]
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
    block_status: BlockStatus = BlockStatus.UNKNOWN
    status_message: str = ""
