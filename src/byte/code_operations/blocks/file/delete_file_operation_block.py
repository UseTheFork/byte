from byte.code_operations import BlockType
from byte.code_operations.blocks.file.base_file_operation_block import BaseFileOperationBlock
from byte.code_operations.schemas import BlockStatus
from byte.files import FileDiscoveryService, FileService
from byte.support import Boundary, BoundaryType
from byte.support.utils import list_to_multiline_text


class DeleteFileOperationBlock(BaseFileOperationBlock):
    """Represents parsed delete operation block."""

    def prepare(self) -> tuple[BlockStatus, str]:
        """Prepare the delete block by validating constraints.

        Returns:
            Tuple of (status, error_message). BlockStatus.VALID if valid, appropriate error status otherwise.

        Usage: `status, error = block.prepare()` -> (BlockStatus.VALID, "") or (BlockStatus.PARSE_ERROR, "error message")
        """
        # Delete blocks should have no content
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
                meta={"path": self.file_path, "operation": BlockType.DELETE, "block_id": self.block_id},  # type:ignore[invalid-argument-type]
            ),
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
            Boundary.open(BoundaryType.ERROR, meta={"operation": BlockType.DELETE, "block_id": self.block_id}),
            f"**File:** `{self.file_path}`",
            f"**Block ID:** {self.block_id}",
            f"**Status:** {self.status}",
            f"**Issue:**\n{self.status_message}",
            Boundary.close(BoundaryType.ERROR),
        ]

        return list_to_multiline_text(sections)

    async def apply(self) -> tuple[BlockStatus, str]:
        """Apply the delete operation to the file system.

        Deletes the file and removes it from both the file discovery service
        and file service context to ensure it's no longer tracked.

        Returns:
            Tuple of (status, error_message). BlockStatus.APPLIED if successful,
            appropriate error status otherwise with error message.

        Usage: `status, error = block.apply()` -> (BlockStatus.APPLIED, "") or (BlockStatus.INVALID, "error message")
        """
        try:
            file_discovery_service: FileDiscoveryService = self.app.make(FileDiscoveryService)
            file_service: FileService = self.app.make(FileService)

            self.resolved_file_path.unlink()

            # Remove the deleted file from context
            await file_discovery_service.remove_file(self.resolved_file_path)
            await file_service.remove_file(str(self.resolved_file_path))

            return BlockStatus.APPLIED, ""

        except (OSError, UnicodeEncodeError) as e:
            return BlockStatus.INVALID, f"Failed to delete file: {e!s}"
