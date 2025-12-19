import re

from langchain_core.messages import AIMessage, RemoveMessage
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.core.logging import log
from byte.core.utils import extract_content_from_message, get_last_message, list_to_multiline_text
from byte.domain.agent.nodes.base_node import Node
from byte.domain.agent.schemas import AssistantContextSchema
from byte.domain.agent.state import BaseState
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.prompt_format.constants import EDIT_BLOCK_NAME
from byte.domain.prompt_format.exceptions import NoBlocksFoundError, PreFlightCheckError, PreFlightUnparsableError
from byte.domain.prompt_format.schemas import BlockStatus, BlockType, RawSearchReplaceBlock, SearchReplaceBlock
from byte.domain.prompt_format.service.edit_format_service import EditFormatService


class ParseBlocksNode(Node):
    """Parse and validate edit blocks from assistant messages.

    This node handles the complete lifecycle of edit block processing:
    1. Validates raw block syntax (block_id, balanced tags)
    2. Parses raw blocks into structured SearchReplaceBlock objects
    3. Validates blocks against the file system
    4. Returns to assistant for corrections if validation fails
    5. Applies valid blocks and proceeds to linting

    Supports iterative correction by merging blocks across multiple scratch_messages
    using block_id as the merge key.

    Usage: Automatically invoked by LangGraph after assistant generates edit blocks.
    """

    def _create_remove_messages(self, messages: list) -> list[RemoveMessage]:
        """Create RemoveMessage objects for messages with valid IDs.

        Usage: `remove_messages = self._create_remove_messages(state["scratch_messages"])`
        """
        return [RemoveMessage(id=msg.id) for msg in messages if msg.id is not None]

    async def _parse_message_to_components(self, message) -> list[str | RawSearchReplaceBlock]:
        """Parse a single AIMessage into interleaved text and raw blocks.

        Returns:
            List containing text strings and RawSearchReplaceBlock objects in order
        """

        content = extract_content_from_message(message)

        # Pattern to match file blocks with block_id
        pattern = (
            r'<file\s+([^>]*block_id="([^"]+)"[^>]*)>\s*<search>(.*?)</search>\s*<replace>(.*?)</replace>\s*</file>'
        )

        result = []
        last_end = 0

        for match in re.finditer(pattern, content, re.DOTALL):
            # Capture text before this block
            text_before = content[last_end : match.start()].strip()
            if text_before:
                result.append(text_before)

            # Extract block components
            block_id = match.group(2)
            raw_content = match.group(0)

            result.append(
                RawSearchReplaceBlock(
                    block_id=block_id, raw_content=raw_content, block_status=BlockStatus.VALID, status_message=""
                )
            )

            last_end = match.end()

        # Capture any remaining text after last block
        text_after = content[last_end:].strip()
        if text_after:
            result.append(text_after)

        return result

    def _merge_components_by_block_id(
        self, base_components: list[str | RawSearchReplaceBlock], new_blocks: list[RawSearchReplaceBlock]
    ) -> list[str | RawSearchReplaceBlock]:
        """Merge new blocks into base components, replacing by block_id.

        Args:
            base_components: Current list of text strings and blocks
            new_blocks: New blocks to merge in (replace matching block_ids)

        Returns:
            Updated list of components with replaced blocks
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
            elif isinstance(component, RawSearchReplaceBlock):
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

    async def _build_final_message_from_iterations(self, state: BaseState) -> list[str | RawSearchReplaceBlock]:
        """Build final message content by applying iterative corrections from scratch_messages.

        Returns:
            List containing interleaved text strings and RawSearchReplaceBlock objects
        """

        ai_messages = [msg for msg in state["scratch_messages"] if isinstance(msg, AIMessage)]
        if not ai_messages:
            return []

        # Parse first message to establish base
        first_message = ai_messages[0]
        base_components = await self._parse_message_to_components(first_message)

        # Process remaining messages
        for message in ai_messages[1:]:
            new_components = await self._parse_message_to_components(message)

            # Extract just the blocks from new_components
            new_blocks = [c for c in new_components if isinstance(c, RawSearchReplaceBlock)]

            # Replace matching blocks in base_components by block_id
            base_components = self._merge_components_by_block_id(base_components, new_blocks)

        return base_components

    async def _parse_to_raw_blocks(
        self,
        state: BaseState,
    ) -> Command | list[str | RawSearchReplaceBlock]:
        # Build final message from all iterations
        final_components = await self._build_final_message_from_iterations(state)

        # Check for failed blocks
        failed_blocks = [
            component
            for component in final_components
            if isinstance(component, RawSearchReplaceBlock) and component.block_status != BlockStatus.VALID
        ]

        # Combine all components into a single string for the new AIMessage
        combined_content_parts = []
        for component in final_components:
            if isinstance(component, str):
                combined_content_parts.append(component)
            elif isinstance(component, RawSearchReplaceBlock):
                combined_content_parts.append(component.raw_content)

        combined_content = "\n".join(combined_content_parts)

        # Create RemoveMessage for all existing scratch_messages
        remove_messages = self._create_remove_messages(state["scratch_messages"])

        # Create new AIMessage with combined content
        new_ai_message = AIMessage(content=combined_content)

        # If there are failed blocks, create error message and return to assistant
        if failed_blocks:
            error_parts = []
            for block in failed_blocks:
                error_parts.append(f"Block ID: {block.block_id}")
                error_parts.append(f"Status: {block.block_status.value}")
                error_parts.append(f"Issue: {block.status_message}")
                error_parts.append(f"\n{block.raw_content}\n")

            error_message = list_to_multiline_text(
                [
                    f"The following {len(failed_blocks)} *{EDIT_BLOCK_NAME}* failed validation:",
                    "",
                    "\n".join(error_parts),
                    "",
                    "No changes were applied.",
                    f"Reply with ONLY the corrected *{EDIT_BLOCK_NAME}* that failed validation.",
                    # self.runtime.context.recovery_steps or "",
                ]
            )

            self.console.print_warning_panel(error_message, title="Validation Error")

            return Command(
                goto="assistant_node",
                update={
                    "scratch_messages": remove_messages + [new_ai_message],
                    "errors": error_message,
                    "metadata": self.metadata,
                },
            )

        # All blocks valid, update scratch_messages and continue
        return final_components

    async def _validate_raw_blocks(
        self,
        state: BaseState,
    ) -> Command | None:
        last_message = get_last_message(state["scratch_messages"])
        response_text = extract_content_from_message(last_message)

        try:
            await self.edit_format.edit_block_service.check_blocks_exist(response_text)
            await self.edit_format.edit_block_service.check_block_ids(response_text)
            await self.edit_format.edit_block_service.check_file_tags_balanced(response_text)
        except Exception as e:
            if isinstance(e, NoBlocksFoundError):
                return Command(goto="end_node")

            if isinstance(e, PreFlightUnparsableError):
                self.console.print_warning_panel(str(e), title="Parse Error: Missing block_id")

                error_message = list_to_multiline_text(
                    [
                        f"Your *{EDIT_BLOCK_NAME}* are malformed:",
                        "```",
                        str(e),
                        "```",
                        "No changes were applied. Add block_id to all blocks and retry.",
                        f"Reply with ONLY the corrected *{EDIT_BLOCK_NAME}*.",
                        self.runtime.context.recovery_steps or "",
                    ]
                )

                return Command(goto="assistant_node", update={"errors": error_message, "metadata": self.metadata})

            if isinstance(e, PreFlightCheckError):
                self.console.print_warning_panel(str(e), title="Parse Error: Pre-flight check failed")

                error_message = list_to_multiline_text(
                    [
                        f"Your *{EDIT_BLOCK_NAME}* failed pre-flight validation:",
                        "```",
                        str(e),
                        "```",
                        "No changes were applied. Fix the malformed blocks and retry with corrected syntax.",
                        f"Reply with ALL *{EDIT_BLOCK_NAME}* (corrected and uncorrected) plus any other content from your original message.",
                        self.runtime.context.recovery_steps or "",
                    ]
                )

                return Command(goto="assistant_node", update={"errors": error_message, "metadata": self.metadata})

            log.exception(e)
            raise

    async def _parse_single_raw_block(self, raw_block: RawSearchReplaceBlock) -> SearchReplaceBlock:
        """Parse a single RawSearchReplaceBlock into a SearchReplaceBlock.

        Uses the existing regex pattern from ParserService to extract structured data.
        """
        # Use the same pattern from ParserService
        pattern = self.edit_format.edit_block_service.match_pattern

        match = re.search(pattern, raw_block.raw_content, re.DOTALL)

        if not match:
            # This shouldn't happen if validation passed, but handle gracefully
            raise ValueError(f"Failed to parse raw block {raw_block.block_id}")

        attr_string, search_content, replace_content = match.groups()

        # Parse attributes (reuse logic from ParserService._parse_attributes)
        attrs = self.edit_format.edit_block_service._parse_attributes(attr_string)

        file_path = attrs.get("path", "").strip()
        operation = attrs.get("operation", "").strip()

        # Determine block type
        block_type_map = {
            "delete": BlockType.REMOVE,
            "replace": BlockType.REPLACE,
            "create": BlockType.ADD,
            "edit": BlockType.EDIT,
        }
        block_type = block_type_map.get(operation, BlockType.EDIT)

        return SearchReplaceBlock(
            block_id=raw_block.block_id,
            file_path=file_path,
            search_content=search_content,
            replace_content=replace_content,
            block_type=block_type,
            block_status=raw_block.block_status,
            status_message=raw_block.status_message,
        )

    async def _parse_raw_blocks_to_search_replace_blocks(
        self,
        components: list[str | RawSearchReplaceBlock],
    ) -> list[str | SearchReplaceBlock]:
        """Parse raw blocks into structured SearchReplaceBlock objects.

        Args:
            components: List of text strings and RawSearchReplaceBlock objects

        Returns:
            List of text strings and SearchReplaceBlock objects
        """
        result = []

        for component in components:
            if isinstance(component, str):
                # Keep text strings unchanged
                result.append(component)
            elif isinstance(component, RawSearchReplaceBlock):
                # Parse the raw content into a SearchReplaceBlock
                parsed_block = await self._parse_single_raw_block(component)
                result.append(parsed_block)

        return result

    def _components_to_content(self, components: list[str | SearchReplaceBlock]) -> str:
        """Convert components list back to combined content string."""
        parts = []
        for component in components:
            if isinstance(component, str):
                parts.append(component)
            elif isinstance(component, SearchReplaceBlock):
                parts.append(component.to_search_replace_format())
        return "\n".join(parts)

    async def _validate_and_correct_search_replace_blocks(
        self,
        state: BaseState,
        components: list[str | SearchReplaceBlock],
    ) -> Command | list[str | SearchReplaceBlock]:
        """Validate SearchReplaceBlocks and return to assistant for corrections if needed."""

        # Extract just the blocks for validation
        blocks = [c for c in components if isinstance(c, SearchReplaceBlock)]

        # Run mid_flight_check to validate against file system
        validated_blocks = await self.edit_format.edit_block_service.mid_flight_check(blocks)

        # Check for failed blocks
        failed_blocks = [block for block in validated_blocks if block.block_status != BlockStatus.VALID]

        if failed_blocks:
            # Build error message similar to _parse_to_raw_blocks
            error_parts = []
            for block in failed_blocks:
                error_parts.append(f"\n{block.to_error_format()}\n")

            error_message = list_to_multiline_text(
                [
                    f"The following {len(failed_blocks)} *{EDIT_BLOCK_NAME}* failed validation:",
                    "",
                    "\n".join(error_parts),
                    "",
                    "No changes were applied.",
                    f"Reply with ONLY the corrected *{EDIT_BLOCK_NAME}*.",
                    # self.runtime.context.recovery_steps or "",
                ]
            )

            self.console.print_warning_panel(error_message, title="Validation Error")

            # Rebuild components with validated blocks
            updated_components = []
            block_map = {b.block_id: b for b in validated_blocks}
            for component in components:
                if isinstance(component, str):
                    updated_components.append(component)
                elif isinstance(component, SearchReplaceBlock):
                    updated_components.append(block_map[component.block_id])

            # Convert back to combined content for AIMessage
            combined_content = self._components_to_content(updated_components)
            remove_messages = self._create_remove_messages(state["scratch_messages"])

            return Command(
                goto="assistant_node",
                update={
                    "scratch_messages": remove_messages + [AIMessage(content=combined_content)],
                    "errors": error_message,
                    "metadata": self.metadata,
                },
            )

        # All blocks valid
        return components

    async def __call__(self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]):
        """Parse commands from the last assistant message."""
        self.console = await self.make(ConsoleService)
        self.edit_format = await self.make(EditFormatService)
        self.runtime = runtime

        self.metadata = state["metadata"]
        self.metadata.iteration += 1

        if self.metadata.iteration >= 4:
            should_continue = self.console.confirm(
                "Failed to parse blocks after 5 attempts. Continue trying?",
                default=False,
            )
            if not should_continue:
                return Command(goto="end_node")

        # Check to make sure the raw blocks can be parsed in general even if some have errors
        # to be parasable a raw block must have an id and a start / end tag.
        result = await self._validate_raw_blocks(state)
        if isinstance(result, Command):
            return result

        result = await self._parse_to_raw_blocks(state)
        if isinstance(result, Command):
            return result

        # If we made it this far we have valid raw blocks. We can now proceed to creating `SearchReplaceBlock`
        result = await self._parse_raw_blocks_to_search_replace_blocks(result)

        # Validate and potentially correct SearchReplaceBlocks
        result = await self._validate_and_correct_search_replace_blocks(state, result)
        if isinstance(result, Command):
            return result

        # All blocks valid, extract them for application
        parsed_blocks = [c for c in result if isinstance(c, SearchReplaceBlock)]

        # Apply the blocks
        parsed_blocks = await self.edit_format.edit_block_service.apply_blocks(parsed_blocks)

        # Assemble final scratch message combining all content and correct blocks
        final_components = []
        block_map = {b.block_id: b for b in parsed_blocks}

        # Rebuild components with applied blocks
        for component in result:
            if isinstance(component, str):
                final_components.append(component)
            elif isinstance(component, SearchReplaceBlock):
                final_components.append(block_map[component.block_id])

        # Convert to combined content for final AIMessage
        final_content = self._components_to_content(final_components)

        # Create RemoveMessage for all existing scratch_messages
        remove_messages = self._create_remove_messages(state["scratch_messages"])

        # Create final AIMessage with combined content
        final_ai_message = AIMessage(content=final_content)

        return Command(
            goto="lint_node",
            update={
                "scratch_messages": remove_messages + [final_ai_message],
                "parsed_blocks": parsed_blocks,
                "metadata": self.metadata,
            },
        )
