import re
from abc import ABC
from pathlib import Path
from typing import List

from langchain_core.messages import AIMessage, BaseMessage

from byte import Service
from byte.code_operations import (
    EDIT_BLOCK_NAME,
    BlockStatus,
    BlockType,
    EditFormatPrompts,
    NoBlocksFoundError,
    PreFlightUnparsableError,
    SearchReplaceBlock,
)
from byte.files import FileDiscoveryService, FileMode, FileService
from byte.support import Boundary, BoundaryType
from byte.support.mixins import UserInteractive
from byte.support.utils import list_to_multiline_text


class EditBlockService(Service, UserInteractive, ABC):
    prompts: EditFormatPrompts
    edit_blocks: List[SearchReplaceBlock]

    match_pattern = rf"<{BoundaryType.EDIT_BLOCK}\s+([^>]+)>\s*<{BoundaryType.SEARCH}>(.*?)</{BoundaryType.SEARCH}>\s*<{BoundaryType.REPLACE}>(.*?)</{BoundaryType.REPLACE}>\s*</{BoundaryType.EDIT_BLOCK}>"

    def boot(self):
        self.edit_blocks = []

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
        # <edit_block path="..." operation="...">
        #   <search>...</search>
        #   <replace>...</replace>
        # </edit_block>
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

            # Determine block type based on operation and file existence
            file_path_obj = Path(file_path.strip())
            if not file_path_obj.is_absolute():
                file_path_obj = self.app.path(str(file_path_obj)).resolve()
            else:
                file_path_obj = file_path_obj.resolve()

            # Map operation string to BlockType
            if operation == "delete":
                block_type = BlockType.DELETE
            elif operation == "replace":
                block_type = BlockType.REPLACE
            elif operation == "create":
                block_type = BlockType.CREATE
            elif operation == "edit":
                block_type = BlockType.EDIT
            else:
                # Default to UNKNOWN for unknown operations so we can fail
                block_type = BlockType.UNKNOWN

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

        file_blocks_with_id = re.findall(rf'<{BoundaryType.EDIT_BLOCK}\s+[^>]*block_id="[^"]+', content)
        file_blocks_total = re.findall(rf"<{BoundaryType.EDIT_BLOCK}\s+", content)

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
        file_open_count = len(re.findall(rf"<{BoundaryType.EDIT_BLOCK}\s+[^>]*>", content))

        if file_open_count == 0:
            raise NoBlocksFoundError(f"No {EDIT_BLOCK_NAME} blocks found in content.")

    async def check_file_tags_balanced(self, content: str) -> None:
        """Validate that edit_block opening and closing tags are properly balanced.

        Counts occurrences of opening and closing edit_block tags and raises an exception
        if they don't match, indicating malformed blocks.

        Args:
            content: Content string to validate

        Raises:
            PreFlightUnparsableError: If opening and closing tags don't match
        """
        file_open_count = len(re.findall(rf"<{BoundaryType.EDIT_BLOCK}\s+[^>]*>", content))
        file_close_count = content.count(f"</{BoundaryType.EDIT_BLOCK}>")

        if file_open_count != file_close_count:
            raise PreFlightUnparsableError(
                f"Malformed {EDIT_BLOCK_NAME} blocks:"
                f"<file> tags={file_open_count}, </file> tags={file_close_count}."
                f"Opening and closing tags must match."
            )

    async def check_single_block_tags_balanced(self, raw_content: str) -> tuple[bool, str]:
        """Validate that search/replace tags are balanced in a single block.

        Returns:
            Tuple of (is_valid, error_message)
        """
        search_count = raw_content.count("<search>")
        search_close_count = raw_content.count("</search>")
        replace_count = raw_content.count("<replace>")
        replace_close_count = raw_content.count("</replace>")

        if search_count != search_close_count:
            return False, f"<search> tags={search_count}, </search> tags={search_close_count}"

        if replace_count != replace_close_count:
            return False, f"<replace> tags={replace_count}, </replace> tags={replace_close_count}"

        if search_count != replace_count:
            return False, f"<search> tags={search_count}, <replace> tags={replace_count}"

        return True, ""

    async def _find_search_content_in_file(
        self, search_content: str, replace_content: str, file_content: str
    ) -> tuple[bool, str, str]:
        """Try to find search content in file with progressive fallback strategies.

                Attempts to locate the search content in the file using multiple strategies:
                1. Exact match (no modifications)
                2. Match after stripping leading/trailing newlines
                3. Match after stripping all leading/trailing whitespace

                Args:
                    search_content: The content to search for in the file
                    replace_content: The replacement content (will be stripped if search is stripped)
                    file_content: The full content of the file to search in

                Returns:
                    Tuple of (found, matched_search_content, matched_replace_content)
                    - found: True if content was found, False otherwise
                    - matched_search_content: The search content that matched (potentially stripped)
                    - matched_replace_content: The replace content (stripped if search was stripped)

                Usage: `found, search, replace = await service._find_search_content_in_file(search, replace,
        content)`
        """

        # First try exact match without any stripping
        if search_content and search_content in file_content:
            self.app["log"].debug("Found exact match (no stripping)")
            return True, search_content, replace_content

        # Try stripping newlines as a fallback
        newline_stripped_search = search_content.strip("\n")
        if newline_stripped_search and newline_stripped_search in file_content:
            self.app["log"].debug("Found match after stripping newlines")
            return True, newline_stripped_search, replace_content.strip("\n")

        # Try stripping all whitespace as a fallback
        stripped_search = search_content.strip()
        if stripped_search and stripped_search in file_content:
            self.app["log"].debug("Found match after stripping all whitespace")
            return True, stripped_search, replace_content.strip()

        # No match found with any strategy
        self.app["log"].debug("No match found with any strategy")
        self.app["log"].debug(f"Search content attempted:\n{search_content}")
        return False, search_content, replace_content

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

        file_service: FileService = self.app.make(FileService)

        for block in blocks:
            file_path = Path(block.file_path)

            # If the path is relative, resolve it against the project root
            if not file_path.is_absolute():
                file_path = self.app.root_path(str(file_path)).resolve()
            else:
                file_path = file_path.resolve()

            # Check if block has a valid operation type
            if block.block_type == BlockType.UNKNOWN:
                block.block_status = BlockStatus.INVALID_OPERATION_ERROR
                block.status_message = "Invalid operation type. Valid operations are: edit, add, delete, replace"
                continue

            # Check if file is in read-only context
            file_context = file_service.get_file_context(file_path)

            if file_context and file_context.mode == FileMode.READ_ONLY:
                block.block_status = BlockStatus.READ_ONLY_ERROR
                block.status_message = f"Cannot edit read-only file: {block.file_path}"
                continue

            # Check if file exists
            if file_path.exists():
                # File exists - validate search content can be found

                # Only validate search content for EDIT operations
                if block.block_type == BlockType.EDIT:
                    try:
                        content = file_path.read_text(encoding="utf-8")

                        found, matched_search, matched_replace = await self._find_search_content_in_file(
                            block.search_content,
                            block.replace_content,
                            content,
                        )

                        if not found:
                            block.block_status = BlockStatus.SEARCH_NOT_FOUND_ERROR
                            block.status_message = (
                                f"Search content not found in `{block.file_path}`.\n\n"
                                f"Current File Content:\n```\n{content}\n```"
                            )
                            continue

                        # Update block with matched content (potentially stripped)
                        block.search_content = matched_search
                        block.replace_content = matched_replace

                    except (FileNotFoundError, PermissionError, UnicodeDecodeError):
                        block.block_status = BlockStatus.SEARCH_NOT_FOUND_ERROR
                        block.status_message = f"Cannot read file: {block.file_path}"
                        continue
            else:
                # File doesn't exist - ensure it's within git root
                # Get project root from config
                try:
                    # Use the resolved file_path for the check
                    file_path.relative_to(self.app.root_path().resolve())
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

        # log.info(blocks)

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
            file_discovery_service: FileDiscoveryService = self.app.make(FileDiscoveryService)
            file_service: FileService = self.app.make(FileService)
            for block in blocks:
                file_path = Path(block.file_path)

                # If the path is relative, resolve it against the project root
                if not file_path.is_absolute():
                    file_path = self.app.path(str(file_path)).resolve()
                else:
                    file_path = file_path.resolve()

                self.app["log"].debug(block.block_type)
                self.app["log"].debug(file_path)
                self.app["log"].debug(file_path.exists())

                # Handle operations based on block type first, not operation string
                if block.block_type == BlockType.DELETE:
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

                elif block.block_type == BlockType.CREATE:
                    # Create new file (can be from + or - operation)
                    if await self.prompt_for_confirmation(
                        f"Create new file '{file_path}'?",
                        True,
                    ):
                        file_path.parent.mkdir(parents=True, exist_ok=True)

                        content = block.replace_content.strip("\n")
                        file_path.write_text(content, encoding="utf-8")

                        # Add the newly created file to context as editable
                        await file_discovery_service.add_file(file_path)
                        await file_service.add_file(file_path, FileMode.EDITABLE)

                elif block.block_type == BlockType.REPLACE:
                    # Replace entire file contents
                    if await self.prompt_for_confirmation(
                        f"Replace all contents of '{file_path}'?",
                        True,
                    ):
                        file_path.write_text(block.replace_content, encoding="utf-8")

                elif block.block_type == BlockType.EDIT:
                    # Edit existing file (can be from + or - operation)
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
        self, messages: list[BaseMessage], mask_message_count: int | None = None
    ) -> str:
        # Get mask_message_count from parameter or fall back to config
        mask_count = (
            mask_message_count
            if mask_message_count is not None
            else (self.app["config"].edit_format.mask_message_count if self.app["config"] else 1)
        )

        # Count total AIMessages to determine which ones are in the last N
        ai_message_indices = [i for i, msg in enumerate(messages) if isinstance(msg, AIMessage)]
        total_ai_messages = len(ai_message_indices)

        # Determine the threshold: AIMessages at or after this index should not be masked
        ai_messages_to_preserve = min(mask_count, total_ai_messages)
        preserve_from_ai_index = total_ai_messages - ai_messages_to_preserve

        # Create masked_messages list identical to messages except for processed AIMessages
        masked_messages = [
            Boundary.open(BoundaryType.CONVERSATION_HISTORY),
            Boundary.open(BoundaryType.HEADING),
            "Below is the conversation history between Byte agents and the user.",
            Boundary.open(BoundaryType.HEADING),
        ]
        ai_message_counter = 0

        if not messages:
            masked_messages.append("The conversation history is empty.")
            masked_messages.append(Boundary.close(BoundaryType.CONVERSATION_HISTORY))
            return list_to_multiline_text(masked_messages)

        for message in messages:
            if isinstance(message, AIMessage):
                # Check if this AIMessage is within the last N AIMessages
                is_within_mask_range = ai_message_counter >= preserve_from_ai_index

                if not isinstance(message.content, list) and not is_within_mask_range:
                    # Create a copy of the message with blocks removed
                    masked_content = await self.remove_blocks_from_content(str(message.content))
                    masked_messages.append(masked_content)
                else:
                    # Keep original message unchanged
                    masked_messages.append(message.content)
                ai_message_counter += 1
            else:
                # Keep non-AIMessages unchanged
                masked_messages.append(message.content)

        masked_messages.append(Boundary.notice("You **MUST** consider the conversation history before proceeding."))
        masked_messages.append(Boundary.close(BoundaryType.CONVERSATION_HISTORY))

        return list_to_multiline_text(masked_messages)
