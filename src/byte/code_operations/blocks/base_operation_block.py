from __future__ import annotations

import re
from abc import abstractmethod
from typing import TYPE_CHECKING

from byte.code_operations import BlockStatus
from byte.code_operations.blocks.base import BaseBlock
from byte.support import BoundaryType

if TYPE_CHECKING:
    from byte.foundation import Application


class BaseOperationBlock(BaseBlock):
    """Base class for all block types in the code operations domain.

    Provides abstract interface for formatting blocks as errors and as
    formatted block content. All block types must implement these methods.
    """

    def __init__(self, app: Application, block_id: str, raw_content: str, **kwargs):
        """ """
        super().__init__(app, **kwargs)
        self.block_id = str(block_id)
        self.raw_content = str(raw_content)
        self.attributes = self.prepare_attributes()

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

    @abstractmethod
    async def apply(self) -> tuple[BlockStatus, str]:
        """Apply the block operation to the file system.

        Returns:
            Tuple of (success, error_message). Empty error_message if successful.

        Usage: `success, error = block.apply()` -> (BlockStatus.APPLIED, "") or (BlockStatus.INVALID, "error message")
        """
        pass

    def extract_block_content(self, raw_content: str) -> str:
        """Extract raw content from between edit_block tags.

        Args:
            raw_content: Raw content string containing edit_block pseudo-XML tags

        Returns:
            Content between edit_block tags

        Usage: `content = block.extract_block_content(raw_content)`
        """
        # Extract content between edit_block tags
        pattern = rf"<{BoundaryType.EDIT_BLOCK}\s+[^>]*>(.*?)</{BoundaryType.EDIT_BLOCK}>"
        match = re.search(pattern, raw_content, re.DOTALL)
        content = match.group(1) if match else ""

        return content

    def to_dict(self) -> dict:
        """Serialize operation block to dictionary."""
        data = super().to_dict()
        data["attributes"] = self.attributes
        return data
