from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from langchain_core.messages import AIMessage

from byte.core.event_bus import Payload
from byte.core.mixins.user_interactive import UserInteractive
from byte.core.service.base_service import Service
from byte.domain.edit_format.schemas import (
    BlockStatus,
    BlockType,
    EditFormatPrompts,
    SearchReplaceBlock,
)
from byte.domain.files.models import FileMode
from byte.domain.files.service.discovery_service import FileDiscoveryService
from byte.domain.files.service.file_service import FileService


class BaseParserService(Service, UserInteractive, ABC):
    prompts: EditFormatPrompts

    @abstractmethod
    async def pre_flight_check(self, content: str) -> None:
        pass

    @abstractmethod
    async def parse_content_to_blocks(self, content: str) -> List[SearchReplaceBlock]:
        pass

    @abstractmethod
    async def remove_blocks_from_content(self, content: str) -> str:
        pass

    async def mid_flight_check(self, blocks: List[SearchReplaceBlock]) -> List[SearchReplaceBlock]:
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

            # If the path is relative, resolve it against the project root
            if not file_path.is_absolute() and self._config and self._config.project_root:
                file_path = (self._config.project_root / file_path).resolve()
            else:
                file_path = file_path.resolve()

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
                        block.status_message = f"Search content not found in {block.file_path}"
                        continue
                except (FileNotFoundError, PermissionError, UnicodeDecodeError):
                    block.block_status = BlockStatus.SEARCH_NOT_FOUND_ERROR
                    block.status_message = f"Cannot read file: {block.file_path}"
                    continue
            else:
                # File doesn't exist - ensure it's within git root
                # Get project root from config
                if self._config and self._config.project_root:
                    try:
                        # Use the resolved file_path for the check
                        file_path.relative_to(self._config.project_root.resolve())
                    except ValueError:
                        block.block_status = BlockStatus.FILE_OUTSIDE_PROJECT_ERROR
                        block.status_message = f"New file must be within project root: {block.file_path}"
                        continue

            # If we reach here, the block is valid
            block.block_status = BlockStatus.VALID

        return blocks

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
        await self.pre_flight_check(content)
        blocks = await self.parse_content_to_blocks(content)
        blocks = await self.mid_flight_check(blocks)
        blocks = await self.apply_blocks(blocks)

        return blocks

    async def apply_blocks(self, blocks: List[SearchReplaceBlock]) -> List[SearchReplaceBlock]:
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
            file_discovery_service: FileDiscoveryService = await self.make(FileDiscoveryService)
            file_service: FileService = await self.make(FileService)
            for block in blocks:
                # Only apply blocks that are valid
                if block.block_status != BlockStatus.VALID:
                    continue

                file_path = Path(block.file_path)

                # If the path is relative, resolve it against the project root
                if not file_path.is_absolute() and self._config and self._config.project_root:
                    file_path = (self._config.project_root / file_path).resolve()
                else:
                    file_path = file_path.resolve()

                # Handle operations based on block type first, not operation string
                if block.block_type == BlockType.REMOVE:
                    # Remove file completely
                    if file_path.exists():
                        if await self.prompt_for_confirmation(
                            f"Delete '{file_path}'?",
                            False,
                        ):
                            file_path.unlink()

                            # Remove the deleted file from context
                            await file_discovery_service.remove_file(file_path)
                            await file_service.remove_file(file_path)

                elif block.block_type == BlockType.ADD:
                    # Create new file (can be from + or - operation)
                    if await self.prompt_for_confirmation(
                        f"Create new file '{file_path}'?",
                        True,
                    ):
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        file_path.write_text(block.replace_content, encoding="utf-8")

                        # Add the newly created file to context as editable
                        await file_discovery_service.add_file(file_path)
                        await file_service.add_file(file_path, FileMode.EDITABLE)

                elif block.block_type == BlockType.REPLACE:
                    # Replace entire file contents
                    if await self.prompt_for_confirmation(
                        f"Replace all contents of '{file_path}'?",
                        False,
                    ):
                        file_path.write_text(block.replace_content, encoding="utf-8")

                elif block.block_type == BlockType.EDIT:
                    # Edit existing file (can be from + or - operation)
                    content = file_path.read_text(encoding="utf-8")

                    # For + operation, do search/replace
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

    async def replace_blocks_in_historic_messages_hook(self, payload: Payload) -> Payload:
        state = payload.get("state", False)
        messages = state["messages"]

        # Get mask_message_count from config
        mask_count = self._config.edit_format.mask_message_count if self._config else 1

        # Create masked_messages list identical to messages except for processed AIMessages
        masked_messages = []
        for index, message in enumerate(messages):
            # Only process AIMessages that are not in the last N messages (where N = mask_message_count)
            is_within_mask_range = index >= len(messages) - mask_count

            if isinstance(message, AIMessage) and not isinstance(message.content, list) and not is_within_mask_range:
                # Create a copy of the message with blocks removed
                masked_content = await self.remove_blocks_from_content(str(message.content))
                masked_message = AIMessage(content=masked_content)
                masked_messages.append(masked_message)
            else:
                # Keep original message unchanged
                masked_messages.append(message)

        state["masked_messages"] = masked_messages

        payload = payload.set("state", state)

        return payload
