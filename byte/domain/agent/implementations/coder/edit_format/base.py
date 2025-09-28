from abc import ABC, abstractmethod
from typing import List

from pydantic.dataclasses import dataclass


@dataclass
class EditFormatPrompts:
    """"""

    system: str

    examples: list[tuple[str, str]]


@dataclass
class EditBlock:
    """Represents a single edit operation with file path, search content, and replacement content."""

    file_path: str
    search_content: str
    replace_content: str


class EditFormat(ABC):
    """"""

    prompts: EditFormatPrompts
    edit_blocks: List[EditBlock]

    def __init__(self):
        self.edit_blocks = []

    @abstractmethod
    def parse_content_to_blocks(self, content: str) -> List[EditBlock]:
        """Parse content string into a list of EditBlock objects for find and replace operations.

        Args:
            content: Raw content string containing edit instructions

        Returns:
            List of EditBlock objects representing individual edit operations
        """
        pass
