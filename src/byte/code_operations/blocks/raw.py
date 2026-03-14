from __future__ import annotations

from typing import TYPE_CHECKING

from byte.code_operations import BlockStatus
from byte.code_operations.blocks.base import BaseBlock
from byte.support import Boundary, BoundaryType
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte.foundation import Application


class RawBlock(BaseBlock):
    """Represents raw/unparsed operation block."""

    def __init__(self, app: Application, block_id: str, raw_content: str, **kwargs):
        super().__init__(app, **kwargs)
        self.block_id = block_id
        self.raw_content = str(raw_content)
        self.attributes = self.prepare_attributes()
        self.operation = self.attributes.get("operation", "")

        # Validate the raw block
        status, error_message = self.prepare()
        self.status = status
        self.status_message = error_message

    def prepare(self) -> tuple[BlockStatus, str]:
        """Validate the raw block syntax and required attributes.

        Returns:
            Tuple of (is_valid, error_message). Empty error_message if valid.

        Usage: `valid, error = block.validate()` -> (True, "") or (False, "error message")
        """
        # Validate required attributes
        if not self.operation:
            return BlockStatus.INVALID, "Missing required attribute 'operation' in block"

        # Validate operation is recognized
        # TODO: This should prob be dynamic somehow
        valid_operations = {"edit", "create", "delete", "replace"}
        if self.operation not in valid_operations:
            return (
                BlockStatus.INVALID,
                f"Invalid operation '{self.operation}'. Valid operations are: {','.join(sorted(valid_operations))}",
            )

        return BlockStatus.VALID, ""

    def to_error_format(self) -> str:
        """Format block as an error message for LLM feedback.

        Returns:
            str: Formatted error block string with status information

        Usage: `error_msg = block.to_error_format()` -> formatted error block
        """

        sections = [
            Boundary.open(BoundaryType.ERROR, meta={"operation": str(self.operation), "block_id": str(self.block_id)}),
            f"**Block ID:** {self.block_id}",
            f"**Status:** {self.status}",
            f"**Issue:**\n{self.status_message}",
            Boundary.close(BoundaryType.ERROR),
        ]

        return list_to_multiline_text(sections)

    def to_block_format(self) -> str:
        """Format block as a structured block string.

        Returns:
            str: Formatted block string

        Usage: `formatted = block.to_block_format()` -> formatted block string
        """
        return str(self.raw_content)
