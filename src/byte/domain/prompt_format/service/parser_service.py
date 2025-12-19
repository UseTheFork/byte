import re
from abc import ABC
from pathlib import Path
from typing import List

from langchain_core.messages import AIMessage, BaseMessage

from byte.core.logging import log
from byte.core.mixins.user_interactive import UserInteractive
from byte.core.service.base_service import Service
from byte.domain.files.models import FileMode
from byte.domain.files.service.discovery_service import FileDiscoveryService
from byte.domain.files.service.file_service import FileService
from byte.domain.prompt_format.constants import EDIT_BLOCK_NAME
from byte.domain.prompt_format.exceptions import NoBlocksFoundError, PreFlightCheckError, PreFlightUnparsableError
from byte.domain.prompt_format.schemas import (
    BlockStatus,
    BlockType,
    BoundaryType,
    EditFormatPrompts,
    RawSearchReplaceBlock,
    SearchReplaceBlock,
)
from byte.domain.prompt_format.service.parser_service_prompt import (
    edit_format_enforcement,
    edit_format_recovery_steps,
    edit_format_system,
    practice_messages,
)
from byte.domain.prompt_format.utils import Boundary


class ParserService(Service, UserInteractive, ABC):
    prompts: EditFormatPrompts
    edit_blocks: List[SearchReplaceBlock]
    match_pattern = r"<file\s+([^>]+)>\s*<search>(.*?)</search>\s*<replace>(.*?)</replace>\s*</file>"

    async def boot(self):
        self.edit_blocks = []
        self.prompts = EditFormatPrompts(
            system=edit_format_system,
            enforcement=edit_format_enforcement,
            recovery_steps=edit_format_recovery_steps,
            examples=practice_messages,
        )

    async def remove_blocks_from_content(self, content: str) -> str:
        """Remove pseudo-XML blocks from content and replace with summary message.

        Identifies all pseudo-XML file blocks in the content and replaces them with
        a concise message indicating changes were applied. Preserves any text
        outside of the blocks.

        Args:
                content: Content string containing pseudo-XML blocks

        Returns:
                str: Content with blocks replaced by summary messages

        Usage: `cleaned = service.remove_blocks_from_content(ai_response)`
        """
        # Pattern to match pseudo-XML file blocks
        pattern = self.match_pattern

        def replacement(match):
            return f"*[Code change removed for brevity. Refer to `{Boundary.open(BoundaryType.CONTEXT, meta={'type': 'editable files'})}`.]*"

        # Replace all blocks with summary messages
        cleaned_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

        return cleaned_content

    def _parse_attributes(self, attr_string: str) -> dict[str, str]:
        """Parse XML-style attributes from a string.

        Args:
            attr_string: String containing attributes like 'key="value" key2="value2"'

        Returns:
            Dictionary mapping attribute names to values
        """
        attrs = {}
        attr_pattern = r'(\w+)="([^"]*)"'
        for match in re.finditer(attr_pattern, attr_string):
            attrs[match.group(1)] = match.group(2)
        return attrs

    async def parse_content_to_blocks(self, content: str) -> List[SearchReplaceBlock]:
        """Extract SEARCH/REPLACE blocks from AI response content.

        Parses pseudo-XML blocks containing file operations with search/replace content.
        Handles empty search/replace sections gracefully.

        Args:
                content: Raw content string containing pseudo-XML blocks

        Returns:
                List of SearchReplaceBlock objects parsed from the content

        Usage: `blocks = service.parse_content_to_blocks(ai_response)`
        """

        blocks = []

        # Pattern to match pseudo-XML file blocks with search/replace content
        # <file path="..." operation="...">
        #   <search>...</search>
        #   <replace>...</replace>
        # </file>
        pattern = self.match_pattern

        matches = re.findall(pattern, content, re.DOTALL)

        for match in matches:
            attr_string, search_content, replace_content = match

            # Parse attributes from the tag
            attrs = self._parse_attributes(attr_string)

            # Extract required attributes
            block_id = attrs.get("block_id", "").strip()
            file_path = attrs.get("path", "").strip()
            operation = attrs.get("operation", "").strip()

            # Strip leading/trailing whitespace but preserve internal structure
            # search_content = search_content.strip()
            # replace_content = replace_content.strip()

            # TODO: Improve logging here.
            log.debug(block_id)
            log.debug(operation)
            log.debug(file_path)
            log.debug(search_content)

            # Determine block type based on operation and file existence
            file_path_obj = Path(file_path.strip())
            if not file_path_obj.is_absolute() and self._config and self._config.project_root:
                file_path_obj = (self._config.project_root / file_path_obj).resolve()
            else:
                file_path_obj = file_path_obj.resolve()

            # Map operation string to BlockType
            if operation == "delete":
                block_type = BlockType.REMOVE
            elif operation == "replace":
                block_type = BlockType.REPLACE
            elif operation == "create":
                block_type = BlockType.ADD
            elif operation == "edit":
                block_type = BlockType.EDIT
            else:
                # Default to EDIT for unknown operations
                block_type = BlockType.EDIT

            blocks.append(
                SearchReplaceBlock(
                    block_id=block_id.strip(),
                    file_path=file_path.strip(),
                    search_content=search_content,
                    replace_content=replace_content,
                    block_type=block_type,
                )
            )
        return blocks

    async def check_block_ids(self, content: str) -> None:
        """Validate that all file blocks have a block_id attribute.

        Checks that every <file> tag includes a block_id attribute and raises
        an exception if any blocks are missing this required identifier.
        """

        file_blocks_with_id = re.findall(r'<file\s+[^>]*block_id="[^"]+', content)
        file_blocks_total = re.findall(r"<file\s+", content)

        blocks_with_id_count = len(file_blocks_with_id)
        total_blocks_count = len(file_blocks_total)

        if blocks_with_id_count < total_blocks_count:
            raise PreFlightUnparsableError(
                f"Malformed {EDIT_BLOCK_NAME} blocks: "
                f"{total_blocks_count - blocks_with_id_count} block(s) missing block_id attribute. "
                f"All file blocks must include a block_id."
            )

    async def check_blocks_exist(self, content: str) -> None:
        """Check if any edit blocks exist in the content.

        Raises NoBlocksFoundError if no file blocks are found.
        """
        file_open_count = len(re.findall(r"<file\s+[^>]*>", content))

        if file_open_count == 0:
            raise NoBlocksFoundError(f"No {EDIT_BLOCK_NAME} blocks found in content.")

    async def check_file_tags_balanced(self, content: str) -> None:
        """foo"""
        file_open_count = len(re.findall(r"<file\s+[^>]*>", content))
        file_close_count = content.count("</file>")

        if file_open_count != file_close_count:
            raise PreFlightUnparsableError(
                f"Malformed {EDIT_BLOCK_NAME} blocks: "
                f"<file> tags={file_open_count}, </file> tags={file_close_count}. "
                f"Opening and closing tags must match."
            )

    async def parse_content_to_raw_blocks(self, content: str) -> list[RawSearchReplaceBlock]:
        """Validate that block markers are properly balanced.

        Counts occurrences of required XML tags and raises an exception
        if they don't match, indicating malformed blocks.
        """

        # AI: how do you suggest we modify this method. it should perform the initial parsing

        file_open_count = len(re.findall(r"<file\s+[^>]*>", content))
        file_close_count = content.count("</file>")
        search_count = content.count("<search>")
        search_close_count = content.count("</search>")
        replace_count = content.count("<replace>")
        replace_close_count = content.count("</replace>")

        if file_open_count != file_close_count:
            raise PreFlightCheckError(
                f"Malformed {EDIT_BLOCK_NAME} blocks: "
                f"<file> tags={file_open_count}, </file> tags={file_close_count}. "
                f"Opening and closing tags must match."
            )

        if search_count != search_close_count:
            raise PreFlightCheckError(
                f"Malformed {EDIT_BLOCK_NAME} blocks: "
                f"<search> tags={search_count}, </search> tags={search_close_count}. "
                f"Opening and closing tags must match."
            )

        if replace_count != replace_close_count:
            raise PreFlightCheckError(
                f"Malformed {EDIT_BLOCK_NAME} blocks: "
                f"<replace> tags={replace_count}, </replace> tags={replace_close_count}. "
                f"Opening and closing tags must match."
            )

        if search_count != replace_count:
            raise PreFlightCheckError(
                f"Malformed {EDIT_BLOCK_NAME} blocks: "
                f"<search> tags={search_count}, <replace> tags={replace_count}. "
                f"Each file block must have matching search and replace tags."
            )

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
                        # Try stripping whitespace as a fallback
                        stripped_search = block.search_content.strip()

                        if stripped_search and stripped_search in content:
                            # Match found after stripping - update the block's search content
                            block.search_content = stripped_search
                            block.replace_content = block.replace_content.strip()
                            # Continue to next validation (block remains VALID)
                        else:
                            # Still no match even after stripping
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

        blocks = await self.parse_content_to_blocks(content)
        blocks = await self.mid_flight_check(blocks)

        log.info(blocks)

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
                            True,
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

    async def replace_blocks_in_historic_messages_hook(
        self, messages: list[BaseMessage], mask_message_count: int | None = None
    ) -> list[BaseMessage]:
        # Get mask_message_count from parameter or fall back to config
        mask_count = (
            mask_message_count
            if mask_message_count is not None
            else (self._config.edit_format.mask_message_count if self._config else 1)
        )

        # Count total AIMessages to determine which ones are in the last N
        ai_message_indices = [i for i, msg in enumerate(messages) if isinstance(msg, AIMessage)]
        total_ai_messages = len(ai_message_indices)

        # Determine the threshold: AIMessages at or after this index should not be masked
        ai_messages_to_preserve = min(mask_count, total_ai_messages)
        preserve_from_ai_index = total_ai_messages - ai_messages_to_preserve

        # Create masked_messages list identical to messages except for processed AIMessages
        masked_messages = []
        ai_message_counter = 0

        for message in messages:
            if isinstance(message, AIMessage):
                # Check if this AIMessage is within the last N AIMessages
                is_within_mask_range = ai_message_counter >= preserve_from_ai_index

                if not isinstance(message.content, list) and not is_within_mask_range:
                    # Create a copy of the message with blocks removed
                    masked_content = await self.remove_blocks_from_content(str(message.content))
                    masked_message = AIMessage(content=masked_content)
                    masked_messages.append(masked_message)
                else:
                    # Keep original message unchanged
                    masked_messages.append(message)

                ai_message_counter += 1
            else:
                # Keep non-AIMessages unchanged
                masked_messages.append(message)

        return masked_messages
