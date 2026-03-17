from __future__ import annotations

from abc import abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

from byte.code_operations.blocks.base_operation_block import BaseOperationBlock
from byte.code_operations.schemas import BlockStatus
from byte.files import FileMode, FileService

if TYPE_CHECKING:
    from byte.foundation import Application


class BaseFileOperationBlock(BaseOperationBlock):
    """Base class for parsed operation blocks (create, delete, edit, replace).

    Extends BaseBlock with validation capabilities for blocks that have been
    parsed and need semantic validation against the file system.
    """

    def _prepare_file_path(self) -> tuple[BlockStatus, str]:
        """Validate file path exists and is not read-only.

        Returns:
            Tuple of (is_valid, status_or_message). BlockStatus if invalid, empty string if valid.

        Usage: `valid, status = self._validate_file_path()` -> (BlockStatus, "") or (BlockStatus, MESSAGE)
        """

        file_path = self.attributes.get("path")
        self.app["log"].info(file_path)
        if not file_path:
            return (
                BlockStatus.INVALID,
                "file_path is required for this operation",
            )

        # Validate file_path type
        if not isinstance(file_path, (str, Path)):
            return (
                BlockStatus.INVALID,
                f"Invalid file_path type: expected str, Path, or PathLike, got {type(file_path).__name__}",
            )

        file_service = self.app.make(FileService)

        file_path = Path(file_path)

        # If the path is relative, resolve it against the project root
        if not file_path.is_absolute():
            resolved_file_path = self.app.root_path(str(file_path)).resolve()
        else:
            resolved_file_path = file_path.resolve()

        # Check if file is in read-only context
        file_context = file_service.get_file_context(resolved_file_path)

        if file_context and file_context.mode == FileMode.READ_ONLY:
            return (
                BlockStatus.INVALID,
                f"Cannot edit read-only file: {file_path}",
            )

        # Check if file is outside project
        project_root = Path(self.app.root_path())

        try:
            resolved_file_path.resolve().relative_to(project_root.resolve())
        except ValueError as e:
            return (
                BlockStatus.INVALID,
                f"File is outside project root: {file_path} {e}",
            )

        self.file_path = str(file_path)
        self.resolved_file_path = resolved_file_path

        return BlockStatus.VALID, ""

    def __init__(self, app: Application, block_id: str, raw_content: str, **kwargs):
        """Initialize parsed block by extracting file_path and operation.

        Args:
            app: Application instance for accessing services
            block_id: Unique identifier for the block
            raw_content: Raw XML content of the block
            file_path: Optional file path to set on the block

        Usage: Called by subclass constructors to initialize base attributes
        """
        super().__init__(app, block_id, raw_content, **kwargs)
        self.content = ""

        # Validate file path semantics before preparing
        status, error_message = self._prepare_file_path()
        if status != BlockStatus.VALID:
            self.status = status
            self.status_message = error_message
            return

        # Validate the block and set status
        status, error_message = self.prepare()
        if status != BlockStatus.VALID:
            self.status = status
            self.status_message = error_message
        else:
            self.status = BlockStatus.VALID

    @abstractmethod
    def prepare(self) -> tuple[BlockStatus, str]:
        """Prepare the create block by validating constraints and loading necessary content.

        Returns:
            Tuple of (status, error_message). BlockStatus.VALID if valid, appropriate error status otherwise.

        Usage: `status, error = block.prepare()` -> (BlockStatus.VALID, "") or (BlockStatus.PARSE_ERROR, "error message")
        """
        pass

    def to_dict(self) -> dict:
        """Serialize file operation block to dictionary."""
        data = super().to_dict()
        data["file_path"] = str(self.file_path) if hasattr(self, "file_path") else None
        data["resolved_file_path"] = str(self.resolved_file_path) if hasattr(self, "resolved_file_path") else None
        data["content"] = str(self.content)
        return data
