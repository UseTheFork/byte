from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from byte.code_operations.schemas import BlockStatus
from byte.support import BoundaryType

if TYPE_CHECKING:
    from byte.foundation import Application


class BaseBlock(ABC):
    """Base class for all block types in the code operations domain.

    Provides abstract interface for formatting blocks as errors and as
    formatted block content. All block types must implement these methods.
    """

    def __init__(self, app: Application, **kwargs):
        """ """
        self.app = app
        self.block_id = ""
        self.raw_content = ""

        self.status = BlockStatus.UNKNOWN
        self.status_message = None

    def prepare_attributes(self) -> dict[str, str]:
        """Extract all attributes from the opening tag and store them as a dict.

            Returns:
                Dictionary of all attribute key-value pairs found in the opening tag

            Usage: `attrs = block.extract_all_attributes()` -> {'path': 'file.py', 'operation': 'edit',
        'block_id': '1'}
        """
        attr_pattern = rf"<{BoundaryType.EDIT_BLOCK}\s+([^>]*?)>"
        attr_match = re.search(attr_pattern, self.raw_content)

        if not attr_match:
            return {}

        attr_string = attr_match.group(1)

        # Match all key="value" pairs
        pattern = r'(\w+)="([^"]*)"'
        matches = re.findall(pattern, attr_string)

        # Convert list of tuples to dict
        attributes = dict(matches)

        return attributes

    @abstractmethod
    def to_error_format(self) -> str:
        """Format block as an error message for LLM feedback.

        Returns:
            str: Formatted error block string with status information

        Usage: `error_msg = block.to_error_format()` -> formatted error block
        """
        pass

    @abstractmethod
    def to_block_format(self) -> str:
        """Format block as a structured block string.

        Returns:
            str: Formatted block string

        Usage: `formatted = block.to_block_format()` -> formatted block string
        """
        pass

    def to_dict(self) -> dict:
        """Serialize block to dictionary for state storage.

        Returns:
            Dictionary representation of the block

        Usage: `block_dict = block.to_dict()`
        """
        return {
            "block_id": self.block_id,
            "raw_content": self.raw_content,
            "status": self.status.value,
            "status_message": self.status_message,
            "block_type": self.__class__.__name__,
        }
