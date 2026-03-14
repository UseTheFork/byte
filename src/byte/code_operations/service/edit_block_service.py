import re
from typing import List

from langchain_core.messages import AIMessage, BaseMessage

from byte import Service
from byte.code_operations import (
    BaseOperationBlock,
    EditFormatPrompts,
    RawBlock,
)
from byte.code_operations.blocks.file.create_file_operation_block import CreateFileOperationBlock
from byte.code_operations.blocks.file.delete_file_operation_block import DeleteFileOperationBlock
from byte.code_operations.blocks.file.edit_file_operation_block import EditFileOperationBlock
from byte.code_operations.blocks.file.replace_file_operation_block import ReplaceFileOperationBlock
from byte.support import Boundary, BoundaryType
from byte.support.mixins import UserInteractive
from byte.support.utils import list_to_multiline_text


class EditBlockService(Service, UserInteractive):
    prompts: EditFormatPrompts

    match_pattern = rf"<{BoundaryType.EDIT_BLOCK}\s+[^>]*>(.*?)</{BoundaryType.EDIT_BLOCK}>"

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

    async def parse_raw_block_to_parsed(self, raw_block: RawBlock) -> BaseOperationBlock:
        """Parse a single RawBlock into a ParsedBlock.

        Args:
            raw_block: Raw block to parse

        Returns:
            Parsed block object (CreateBlock, EditBlock, DeleteFileOperationBlock, or ReplaceBlock)

        Usage: `block = await service.parse_raw_block_to_parsed(raw_block)`
        """

        # Map operation string to block type
        operation = raw_block.operation

        # TODO: Need to throw here but its should not be possible to get here.
        if operation == "create":
            return CreateFileOperationBlock(self.app, raw_block.block_id, raw_block.raw_content)
        elif operation == "edit":
            return EditFileOperationBlock(self.app, raw_block.block_id, raw_block.raw_content)
        elif operation == "delete":
            return DeleteFileOperationBlock(self.app, raw_block.block_id, raw_block.raw_content)
        elif operation == "replace":
            return ReplaceFileOperationBlock(self.app, raw_block.block_id, raw_block.raw_content)

        raise ValueError(f"Invalid operation type: {operation}")

    async def convert_raw_blocks_to_parsed(self, components: list[str | RawBlock]) -> list[str | BaseOperationBlock]:
        """Convert raw blocks in components to ParsedBlock objects.

        Args:
            components: List of text strings and RawBlock objects

        Returns:
            List of text strings and ParsedBlock objects

        """
        result = []

        for component in components:
            if isinstance(component, str):
                # Keep text strings unchanged
                result.append(component)
            elif isinstance(component, RawBlock):
                # Parse the raw content into a ParsedBlock
                parsed_block = await self.parse_raw_block_to_parsed(component)
                result.append(parsed_block)

        return result

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

    async def apply_blocks(self, blocks: List[BaseOperationBlock]) -> List[BaseOperationBlock]:
        """Apply the validated edit blocks to the file system.

        Handles both file creation (ADD blocks) and content modification (EDIT blocks)
        based on the block type determined during mid_flight_check. Only applies blocks
        that have valid status.

        Args:
                blocks: List of validated ParsedBlock objects to apply

        Returns:
                List[ParsedBlock]: The original list of blocks with their status information
        """
        # try:
        # file_discovery_service: FileDiscoveryService = self.app.make(FileDiscoveryService)
        # file_service: FileService = self.app.make(FileService)
        for block in blocks:
            await block.apply()

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
