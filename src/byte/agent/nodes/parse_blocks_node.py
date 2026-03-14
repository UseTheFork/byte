from typing import Literal

from langchain_core.messages import AIMessage, RemoveMessage
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.agent import AssistantContextSchema, BaseState, Node
from byte.cli import InputCancelledError
from byte.code_operations import (
    EDIT_BLOCK_NAME,
    BaseBlock,
    BaseOperationBlock,
    BlockStatus,
    EditBlockService,
    NoBlocksFoundError,
    PreFlightUnparsableError,
    RawBlockService,
)
from byte.support.mixins import UserInteractive
from byte.support.utils import list_to_multiline_text


class ParseBlocksNode(Node, UserInteractive):
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

    def _components_to_content(self, components: list[str | BaseBlock]) -> str:
        """Convert components list back to combined content string."""
        parts = []
        for component in components:
            if isinstance(component, str):
                parts.append(component)
            elif isinstance(component, BaseBlock):
                parts.append(component.to_block_format())
        return "\n".join(parts)

    async def __call__(
        self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]
    ) -> Command[Literal["end_node", "lint_node"]]:
        """Parse commands from the last assistant message."""
        self.console = self.app["console"]
        self.edit_block_service = self.app.make(EditBlockService)
        self.raw_block_service = self.app.make(RawBlockService)
        self.runtime = runtime

        self.metadata = state["metadata"]
        self.metadata.iteration += 1

        if self.metadata.iteration >= 4:
            try:
                should_continue = await self.prompt_for_confirmation(
                    "Failed to parse blocks after 5 attempts. Continue trying?",
                    default=False,
                )

            except InputCancelledError:
                should_continue = False

            if not should_continue:
                # Dont store this invocation in memory
                self.metadata.erase_history = True
                return Command(
                    goto="end_node",
                    update={
                        "metadata": self.metadata,
                    },
                )

        # Parse and merge iterations using RawBlockService
        try:
            final_components = await self.raw_block_service.merge_iterations(state["scratch_messages"])
            self.app["log"].info(final_components)

        except NoBlocksFoundError:
            return Command(goto="end_node")
        except PreFlightUnparsableError as e:
            self.console.print_warning_panel(str(e), title="Parse Error: Missing block_id")

            error_message = list_to_multiline_text(
                [
                    f"Your *{EDIT_BLOCK_NAME}* are malformed:",
                    "```",
                    str(e),
                    "```",
                    "",
                ]
            )

            return Command(goto="assistant_node", update={"errors": error_message, "metadata": self.metadata})

        # Convert raw blocks to BaseOperationBlock using EditBlockService
        components = await self.edit_block_service.convert_raw_blocks_to_parsed(final_components)

        # Extract blocks for validation
        blocks = [c for c in components if isinstance(c, BaseOperationBlock)]

        # Check for failed blocks
        failed_blocks = [block for block in blocks if block.status != BlockStatus.VALID]

        if failed_blocks:
            # Build error message
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
                ]
            )

            self.console.print_warning_panel(error_message, title="Validation Error")

            # Rebuild components with validated blocks
            updated_components = []
            block_map = {b.block_id: b for b in blocks}
            for component in components:
                if isinstance(component, str):
                    updated_components.append(component)
                elif isinstance(component, BaseOperationBlock):
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

        # All blocks valid, apply them
        parsed_blocks = await self.edit_block_service.apply_blocks(blocks)

        self.app["log"].info(f"Successfully applied {len(parsed_blocks)} blocks")

        # Assemble final scratch message combining all content and correct blocks
        final_components = []
        block_map = {b.block_id: b for b in parsed_blocks}

        # Rebuild components with applied blocks
        for component in components:
            if isinstance(component, str):
                final_components.append(component)
            elif isinstance(component, BaseBlock):
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
                "parsed_blocks": [block.to_dict() for block in parsed_blocks],
                "metadata": self.metadata,
            },
        )
