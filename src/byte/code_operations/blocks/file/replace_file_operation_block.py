from byte.code_operations import BlockType
from byte.code_operations.blocks.file.base_file_operation_block import BaseFileOperationBlock
from byte.code_operations.schemas import BlockStatus
from byte.support import Boundary, BoundaryType
from byte.support.utils import list_to_multiline_text


class ReplaceFileOperationBlock(BaseFileOperationBlock):
    """Represents parsed replace operation block."""

    def prepare(self) -> tuple[BlockStatus, str]:
        """Prepare the replace block by validating constraints and loading necessary content.

        Returns:
            Tuple of (status, error_message). BlockStatus.VALID if valid, appropriate error status otherwise.

        Usage: `status, error = block.prepare()` -> (BlockStatus.VALID, "") or (BlockStatus.PARSE_ERROR, "error message")
        """
        self.content = self.extract_block_content(self.raw_content).strip()

        return BlockStatus.VALID, ""

    def to_block_format(self) -> str:
        """Format block as a structured block string.

        Returns:
            str: Formatted block string

        Usage: `formatted = block.to_block_format()` -> formatted block string
        """

        sections = [
            Boundary.open(
                BoundaryType.EDIT_BLOCK,
                meta={"path": self.file_path, "operation": BlockType.REPLACE, "block_id": self.block_id},
            ),
            self.content,
            Boundary.close(BoundaryType.EDIT_BLOCK),
        ]

        return list_to_multiline_text(sections)

    def to_error_format(self) -> str:
        """Format block as an error message for LLM feedback.

        Returns:
            str: Formatted error block string with status information

        Usage: `error_msg = block.to_error_format()` -> formatted error block
        """

        sections = [
            Boundary.open(BoundaryType.ERROR, meta={"operation": BlockType.REPLACE, "block_id": self.block_id}),
            f"**File:** `{self.file_path}`",
            f"**Block ID:** {self.block_id}",
            f"**Status:** {self.status.value}",
            f"**Issue:**\n{self.status_message}",
            Boundary.close(BoundaryType.ERROR),
        ]

        return list_to_multiline_text(sections)

    async def apply(self) -> tuple[BlockStatus, str]:
        """ """
        try:
            if await self.prompt_for_confirmation(
                f"Replace all contents of '{self.file_path}'?",
                True,
            ):
                # Create parent directories if they don't exist
                self.resolved_file_path.parent.mkdir(parents=True, exist_ok=True)

                # Write content to file
                content = self.content.strip("\n")
                self.resolved_file_path.write_text(content, encoding="utf-8")

                return BlockStatus.APPLIED, ""

            return BlockStatus.VALID, ""

        except (OSError, UnicodeEncodeError) as e:
            return BlockStatus.INVALID, f"Failed to create file: {e!s}"
