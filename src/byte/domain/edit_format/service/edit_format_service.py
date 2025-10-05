import re
from enum import Enum
from pathlib import Path
from typing import List

from langchain_core.messages import AIMessage
from pydantic.dataclasses import dataclass

from byte.core.event_bus import Payload
from byte.core.mixins.user_interactive import UserInteractive
from byte.core.service.base_service import Service
from byte.domain.edit_format.exceptions import PreFlightCheckError
from byte.domain.edit_format.service.edit_format_prompt import (
    edit_format_system,
    practice_messages,
)
from byte.domain.files.context_manager import FileMode
from byte.domain.files.service.file_service import FileService


class BlockType(Enum):
    """Type of edit block operation."""

    EDIT = "edit"  # Modify existing file content
    ADD = "add"  # Create new file
    REMOVE = "remove"  # Remove existing file


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

    operation: str
    file_path: str
    search_content: str
    replace_content: str
    block_type: BlockType = BlockType.EDIT
    block_status: BlockStatus = BlockStatus.VALID
    status_message: str = ""

    def to_search_replace_format(
        self,
        fence: str = "```",
        operation: str = "+++++++",
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
{operation} {self.file_path}
{search}
{self.search_content}
{divider}
{self.replace_content}
{replace}
{fence}"""


class EditFormatService(Service, UserInteractive):
    """"""

    add_file_marker: str = "+++++++"
    remove_file_marker: str = "-------"
    search: str = "<<<<<<< SEARCH"
    divider: str = "======="
    replace: str = ">>>>>>> REPLACE"

    prompts: EditFormatPrompts
    edit_blocks: List[SearchReplaceBlock]

    async def boot(self):
        self.edit_blocks = []
        self.prompts = EditFormatPrompts(
            system=edit_format_system, examples=practice_messages
        )

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

    def parse_content_to_blocks(self, content: str) -> List[SearchReplaceBlock]:
        """Extract SEARCH/REPLACE blocks from AI response content."""

        blocks = []

        # Pattern to match the entire SEARCH/REPLACE block structure
        pattern = r"```\w*\n(\+\+\+\+\+\+\+|-------) (.+?)\n<<<<<<< SEARCH\n(.*?)\n=======\n(.*?)\n>>>>>>> REPLACE\n```"

        matches = re.findall(pattern, content, re.DOTALL)

        for match in matches:
            operation, file_path, search_content, replace_content = match
            blocks.append(
                SearchReplaceBlock(
                    operation=operation,
                    file_path=file_path.strip(),
                    search_content=search_content,
                    replace_content=replace_content,
                )
            )
        return blocks

    def remove_blocks_from_content(self, content: str) -> str:
        """Remove SEARCH/REPLACE blocks from content and replace with summary message.

        Identifies all search/replace blocks in the content and replaces them with
        a concise message indicating changes were applied. Preserves any text
        outside of the blocks.

        Args:
            content: Content string containing search/replace blocks

        Returns:
            str: Content with blocks replaced by summary messages

        Usage: `cleaned = service.remove_blocks_from_content(ai_response)`
        """
        # Pattern to match the entire SEARCH/REPLACE block structure
        pattern = r"```\w*\n(\+\+\+\+\+\+\+|-------) (.+?)\n<<<<<<< SEARCH\n(.*?)\n=======\n(.*?)\n>>>>>>> REPLACE\n```"

        def replacement(match):
            operation, file_path, _, _ = match.groups()

            return f"*[Changes applied to `{file_path.strip()}` - search/replace block removed]*"

        # Replace all blocks with summary messages
        cleaned_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

        return cleaned_content

    def pre_flight_check(self, content: str) -> None:
        """Validate that SEARCH/REPLACE block markers are properly balanced.

        Counts occurrences of all five required markers and raises an exception
        if they don't match, indicating malformed blocks.
        """
        search_count = content.count(self.search)
        replace_count = content.count(self.replace)
        divider_count = content.count(self.divider)
        file_marker_count = content.count(self.add_file_marker) + content.count(
            self.remove_file_marker
        )

        if not (search_count == replace_count == divider_count == file_marker_count):
            raise PreFlightCheckError(
                f"Malformed SEARCH/REPLACE blocks: "
                f"SEARCH={search_count}, REPLACE={replace_count}, "
                f"dividers={divider_count}, file markers={file_marker_count}. "
                f"All counts must be equal."
            )

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

            # Set block type based on operation and file existence
            if block.operation == "-------":
                # --- operation: remove file or replace entire contents
                if block.search_content == "" and block.replace_content == "":
                    block.block_type = BlockType.REMOVE  # Remove file completely
                elif file_path.exists():
                    block.block_type = BlockType.EDIT  # Replace entire contents
                else:
                    block.block_type = BlockType.ADD  # Create new file
            else:  # +++ operation
                # +++ operation: edit existing or create new
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

                if block.block_type == BlockType.REMOVE:
                    # Remove file completely
                    if file_path.exists():
                        if await self.prompt_for_confirmation(
                            f"Delete '{file_path}'?",
                            False,
                        ):
                            file_path.unlink()

                elif block.operation == "-------":
                    # ------- operation: replace entire file contents
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    if await self.prompt_for_confirmation(
                        f"Replace all contents of '{file_path}'?",
                        False,
                    ):
                        file_path.write_text(block.replace_content, encoding="utf-8")

                elif block.operation == "+++++++":
                    # +++ operation: edit existing or create new
                    if block.block_type == BlockType.ADD:
                        # Create new file
                        if await self.prompt_for_confirmation(
                            f"Create new file '{file_path}'?",
                            True,
                        ):
                            file_path.parent.mkdir(parents=True, exist_ok=True)
                            file_path.write_text(
                                block.replace_content, encoding="utf-8"
                            )

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

    async def replace_blocks_in_historic_messages_hook(
        self, payload: Payload
    ) -> Payload:
        state = payload.get("state", False)
        messages = state["messages"]

        # Collect all AIMessage indices
        ai_message_indices = [
            i for i, msg in enumerate(messages) if isinstance(msg, AIMessage)
        ]

        # Determine which AIMessages to skip (the last 2)
        indices_to_skip = (
            set(ai_message_indices[-2:])
            if len(ai_message_indices) > 2
            else set(ai_message_indices)
        )

        # Iterate through messages in order
        for index, message in enumerate(messages):
            # Only process AIMessages that are not in the last 2
            if isinstance(message, AIMessage) and index not in indices_to_skip:
                # Remove search/replace blocks and replace with summary
                messages[index].content = self.remove_blocks_from_content(
                    str(message.content)
                )

        return payload
