import re
from typing import List

from langchain.messages import AIMessage

from byte import Service
from byte.code_operations import EDIT_BLOCK_NAME, BlockStatus, NoBlocksFoundError, PreFlightUnparsableError, RawBlock
from byte.support import BoundaryType
from byte.support.utils import extract_content_from_message


class RawBlockService(Service):
    """Service for parsing and validating RawBlock objects.

    This service handles the initial parsing of raw edit block content into
    RawBlock objects and performs syntax validation including:
    - Extracting block_id from edit blocks
    - Validating tag balance (search/replace tags)
    - Checking for required attributes

    Usage: Used by ParseBlocksNode to convert raw content into structured blocks
    """

    async def parse_content_to_raw_blocks(self, content: str) -> List[RawBlock]:
        """Parse content into RawBlock objects.

        Extracts edit blocks from content and creates RawBlock objects
        with initial validation status. Blocks with missing block_id or unbalanced
        tags will be marked with appropriate error status.

        Args:
            content: Raw content string containing edit blocks

        Returns:
            List of RawBlock objects with validation status

        Usage: `raw_blocks = await service.parse_content_to_raw_blocks(content)`
        """
        raw_blocks = []

        await self.check_edit_block_tags_balanced(content)

        # Pattern to match ALL edit_block tags (with or without block_id)
        pattern = rf"<{BoundaryType.EDIT_BLOCK}\s+([^>]*)>(.*?)</{BoundaryType.EDIT_BLOCK}>"

        for match in re.finditer(pattern, content, re.DOTALL):
            attributes = match.group(1)
            raw_content = match.group(0)

            # Extract and validate block_id from attributes
            block_id = await self.extract_and_validate_block_id(attributes)

            raw_blocks.append(
                RawBlock(
                    app=self.app,
                    block_id=block_id,
                    raw_content=raw_content,
                )
            )

        if not raw_blocks:
            raise NoBlocksFoundError(f"No {EDIT_BLOCK_NAME} blocks found in content.")

        return raw_blocks

    async def extract_and_validate_block_id(self, attributes: str) -> str:
        """Extract and validate block_id from edit_block attributes.

        Args:
            attributes: Attribute string from edit_block opening tag

        Returns:
            Validated block_id string

        Raises:
            PreFlightUnparsableError: If block_id is missing, empty, or not a number

        Usage: `block_id = await service.extract_and_validate_block_id(attributes)`
        """
        # Extract block_id from attributes
        block_id_match = re.search(r'block_id="([^"]+)"', attributes)

        if not block_id_match:
            raise PreFlightUnparsableError(f"Malformed {EDIT_BLOCK_NAME} block: missing block_id attribute")

        block_id = block_id_match.group(1)

        # Validate block_id is not empty and is a number
        if not block_id or not block_id.strip():
            raise PreFlightUnparsableError(f"Malformed {EDIT_BLOCK_NAME} block: block_id cannot be empty")

        if not block_id.isdigit():
            raise PreFlightUnparsableError(
                f"Malformed {EDIT_BLOCK_NAME} block: block_id must be a number, got '{block_id}'"
            )

        return block_id

    async def check_edit_block_tags_balanced(self, content: str) -> None:
        """Validate that edit_block tags are balanced in the content.

        Args:
            content: Raw content containing edit blocks

        Raises:
            PreFlightUnparsableError: If edit_block tags are unbalanced

        Usage: `await service.check_edit_block_tags_balanced(content)`
        """
        edit_block_open = content.count(f"<{BoundaryType.EDIT_BLOCK}")
        edit_block_close = content.count(f"</{BoundaryType.EDIT_BLOCK}>")

        if edit_block_open != edit_block_close:
            raise PreFlightUnparsableError(
                f"Opening and closing edit blocks need to match: "
                f"found {edit_block_open} opening <{BoundaryType.EDIT_BLOCK}> tag(s) "
                f"but {edit_block_close} closing </{BoundaryType.EDIT_BLOCK}> tag(s)"
            )

    async def validate_block_ids_exist(self, content: str) -> None:
        """Validate that all file blocks have a block_id attribute.

        Checks that every edit block includes a block_id attribute and raises
        an exception if any blocks are missing this required identifier.

        Args:
            content: Content string to validate

        Raises:
            PreFlightUnparsableError: If any blocks are missing block_id

        Usage: `await service.validate_block_ids_exist(content)`
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

    async def parse_message_to_components(self, message: AIMessage) -> list[str | RawBlock]:
        """Parse a single AIMessage into interleaved text and raw blocks.

        Returns:
            List containing text strings and RawBlock objects in order

        Usage: `components = await service.parse_message_to_components(message)`
        """
        content = extract_content_from_message(message)

        # Parse blocks from content
        try:
            raw_blocks = await self.parse_content_to_raw_blocks(content)
        except NoBlocksFoundError:
            # If no blocks found, return content as text
            return [content.strip()] if content.strip() else []

        # Manually extract text between blocks
        result = []
        last_end = 0

        for block in raw_blocks:
            # Find the position of this block in the content
            block_start = content.find(str(block.raw_content), last_end)

            if block_start == -1:
                # This shouldn't happen, but handle gracefully
                continue

            # Capture text before this block
            text_before = content[last_end:block_start].strip()
            if text_before:
                result.append(text_before)

            # Add the block
            result.append(block)

            last_end = block_start + len(str(block.raw_content))

        # Capture any remaining text after last block
        text_after = content[last_end:].strip()
        if text_after:
            result.append(text_after)

        return result

    async def merge_components_by_block_id(
        self, base_components: list[str | RawBlock], new_blocks: list[RawBlock]
    ) -> list[str | RawBlock]:
        """Merge new blocks into base components, replacing by block_id.

        Args:
            base_components: Current list of text strings and blocks
            new_blocks: New blocks to merge in (replace matching block_ids)

        Returns:
            Updated list of components with replaced blocks

        Usage: `merged = await service.merge_components_by_block_id(base, new)`
        """
        # Create a mapping of block_id to block for quick lookup
        block_map = {block.block_id: block for block in new_blocks}

        result = []
        seen_ids = set()

        # Iterate through base components
        for component in base_components:
            if isinstance(component, str):
                # Keep text strings unchanged
                result.append(component)
            elif isinstance(component, RawBlock):
                # Replace block if we have a new version, otherwise keep original
                if component.block_id in block_map:
                    result.append(block_map[component.block_id])
                    seen_ids.add(component.block_id)
                else:
                    result.append(component)
                    seen_ids.add(component.block_id)

        # Append any new blocks that weren't in base_components
        for new_block in new_blocks:
            if new_block.block_id not in seen_ids:
                result.append(new_block)

        return result

    async def merge_iterations(self, messages: list[AIMessage]) -> list[str | RawBlock]:
        """Build final message content by merging blocks across multiple iterations.

        Args:
            messages: List of AIMessage objects to merge

        Returns:
            List containing interleaved text strings and RawBlock objects

        Usage: `final = await service.merge_iterations(messages)`
        """
        ai_messages = [msg for msg in messages if isinstance(msg, AIMessage)]
        if not ai_messages:
            return []

        # Parse first message to establish base
        first_message = ai_messages[0]
        base_components = await self.parse_message_to_components(first_message)

        self.app["log"].info(base_components)

        # Process remaining messages
        for message in ai_messages[1:]:
            new_components = await self.parse_message_to_components(message)

            # Extract just the blocks from new_components
            new_blocks = [c for c in new_components if isinstance(c, RawBlock)]

            # Replace matching blocks in base_components by block_id
            base_components = await self.merge_components_by_block_id(base_components, new_blocks)

        return base_components

    async def validate_syntax(self, components: list[str | RawBlock]) -> tuple[bool, str, list[RawBlock]]:
        """Validate syntax of raw blocks in components.

        Args:
            components: List of text strings and RawBlock objects

        Returns:
            Tuple of (is_valid, error_message, failed_blocks)

        Usage: `valid, error, failed = await service.validate_syntax(components)`
        """
        # Check for failed blocks
        failed_blocks = [
            component
            for component in components
            if isinstance(component, RawBlock) and component.status != BlockStatus.VALID
        ]

        if failed_blocks:
            # Build error message
            error_parts = []
            for block in failed_blocks:
                error_parts.append(f"Block ID: {block.block_id}")
                error_parts.append(f"Status: {block.status}")
                error_parts.append(f"Issue: {block.status_message}")
                error_parts.append(f"\n{block.raw_content}\n")

            error_message = "\n".join(error_parts)
            return False, error_message, failed_blocks

        return True, "", []
