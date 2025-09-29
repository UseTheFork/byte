from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import List

from pydantic.dataclasses import dataclass

from byte.core.mixins.bootable import Bootable
from byte.core.mixins.configurable import Configurable
from byte.domain.files.context_manager import FileMode
from byte.domain.files.service.file_service import FileService


class BlockType(Enum):
    """Type of edit block operation."""

    EDIT = "edit"  # Modify existing file content
    ADD = "add"  # Create new file


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
class SearchReplaceBlock:
    """Represents a single edit operation with file path, search content, and replacement content."""

    file_path: str
    search_content: str
    replace_content: str
    block_type: BlockType = BlockType.EDIT
    block_status: BlockStatus = BlockStatus.VALID
    status_message: str = ""

    def to_search_replace_format(
        self,
        fence: str = "```",
        file_marker: str = "+++",
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
{file_marker} {self.file_path}
{search}
{self.search_content}
{divider}
{self.replace_content}
{replace}
{fence}"""


class EditFormat(ABC, Bootable, Configurable):
    """"""

    prompts: EditFormatPrompts
    edit_blocks: List[SearchReplaceBlock]

    async def boot(self):
        self.edit_blocks = []

    async def handle(self, content: str) -> List[SearchReplaceBlock]:
        """Process content by validating and parsing it into SearchReplaceBlock objects.

        Performs pre-flight validation checks before parsing to ensure content
        contains properly formatted edit blocks. Returns a list of parsed blocks
        ready for application.

        Args:
            content: Raw content string containing edit instructions

        Returns:
            List of SearchReplaceBlock objects representing individual edit operations

        Raises:
            PreFlightCheckError: If content contains malformed edit blocks
        """
        self.pre_flight_check(content)
        blocks = self.parse_content_to_blocks(content)
        blocks = await self.mid_flight_check(blocks)
        blocks = await self.apply_blocks(blocks)

        return blocks

    @abstractmethod
    def parse_content_to_blocks(self, content: str) -> List[SearchReplaceBlock]:
        """Parse content string into a list of EditBlock objects for find and replace operations.

        Args:
            content: Raw content string containing edit instructions

        Returns:
            List of EditBlock objects representing individual edit operations
        """
        pass

    @abstractmethod
    def pre_flight_check(self, content: str) -> None:
        """Validate edit block structure before parsing.

        Performs validation checks on the raw content to ensure it contains
        properly formatted edit blocks. Should raise PreFlightCheckError
        if validation fails.

        Args:
            content: Raw content string to validate

        Raises:
            PreFlightCheckError: If content contains malformed edit blocks
        """
        pass

    async def mid_flight_check(
        self, blocks: List[SearchReplaceBlock]
    ) -> List[SearchReplaceBlock]:
        """Validate parsed edit blocks against file system and context constraints.

        Performs validation checks on parsed blocks and sets their status instead
        of throwing exceptions. Checks for read-only violations, search content
        matches, and file location constraints.

        Args:
            blocks: List of parsed SearchReplaceBlock objects to validate

        Returns:
            List of SearchReplaceBlock objects with updated status information
        """

        file_service: FileService = await self.make(FileService)

        for block in blocks:
            file_path = Path(block.file_path)

            # Set block type based on file existence
            if file_path.exists():
                block.block_type = BlockType.EDIT
            else:
                block.block_type = BlockType.ADD

            # Check if file is in read-only context
            file_context = file_service.get_file_context(file_path)
            if file_context and file_context.mode == FileMode.READ_ONLY:
                block.block_status = BlockStatus.READ_ONLY_ERROR
                block.status_message = f"Cannot edit read-only file: {block.file_path}"
                continue

            # Check if file exists
            if file_path.exists():
                # File exists - validate search content can be found
                try:
                    content = file_path.read_text(encoding="utf-8")
                    if block.search_content and block.search_content not in content:
                        block.block_status = BlockStatus.SEARCH_NOT_FOUND_ERROR
                        block.status_message = (
                            f"Search content not found in {block.file_path}"
                        )
                        continue
                except (FileNotFoundError, PermissionError, UnicodeDecodeError):
                    block.block_status = BlockStatus.SEARCH_NOT_FOUND_ERROR
                    block.status_message = f"Cannot read file: {block.file_path}"
                    continue
                # TODO: Placeholder for user confirmation on existing files
            else:
                # File doesn't exist - ensure it's within git root
                # Get project root from config
                if self._config and self._config.project_root:
                    try:
                        file_path.resolve().relative_to(
                            self._config.project_root.resolve()
                        )
                    except ValueError:
                        block.block_status = BlockStatus.FILE_OUTSIDE_PROJECT_ERROR
                        block.status_message = (
                            f"New file must be within project root: {block.file_path}"
                        )
                        continue

            # If we reach here, the block is valid
            block.block_status = BlockStatus.VALID

        return blocks

    async def apply_blocks(
        self, blocks: List[SearchReplaceBlock]
    ) -> List[SearchReplaceBlock]:
        """Apply the validated edit blocks to the file system.

        Handles both file creation (ADD blocks) and content modification (EDIT blocks)
        based on the block type determined during mid_flight_check. Only applies blocks
        that have valid status.

        Args:
            blocks: List of validated SearchReplaceBlock objects to apply

        Returns:
            List[SearchReplaceBlock]: The original list of blocks with their status information
        """
        try:
            for block in blocks:
                # Only apply blocks that are valid
                if block.block_status != BlockStatus.VALID:
                    continue

                file_path = Path(block.file_path)

                if block.block_type == BlockType.ADD:
                    # Create new file
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(block.replace_content, encoding="utf-8")

                elif block.block_type == BlockType.EDIT:
                    content = file_path.read_text(encoding="utf-8")

                    # Handle empty search content (append to file)
                    if not block.search_content:
                        new_content = content + block.replace_content
                    else:
                        # Replace first occurrence of search content
                        new_content = content.replace(
                            block.search_content,
                            block.replace_content,
                            1,  # Only replace first occurrence
                        )

                    file_path.write_text(new_content, encoding="utf-8")

        except (OSError, UnicodeDecodeError, UnicodeEncodeError):
            # Handle file I/O errors gracefully - blocks retain their original status
            pass

        return blocks
