from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.core.logging import log
from byte.core.utils import extract_content_from_message, get_last_message, list_to_multiline_text
from byte.domain.agent.nodes.base_node import Node
from byte.domain.agent.schemas import AssistantContextSchema
from byte.domain.agent.state import BaseState
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.prompt_format.exceptions import NoBlocksFoundError, PreFlightCheckError
from byte.domain.prompt_format.schemas import BlockStatus
from byte.domain.prompt_format.service.edit_format_service import EditFormatService


class ParseBlocksNode(Node):
    async def boot(self, edit_format: EditFormatService, **kwargs):
        self.edit_format = edit_format

    async def __call__(self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]):
        """Parse commands from the last assistant message."""
        console = await self.make(ConsoleService)

        metadata = state["metadata"]
        metadata.iteration += 1

        if metadata.iteration >= 5:
            should_continue = console.confirm(
                "Failed to parse blocks after 5 attempts. Continue trying?",
                default=False,
            )
            if not should_continue:
                return Command(goto="end_node")

        last_message = get_last_message(state["scratch_messages"])
        response_text = extract_content_from_message(last_message)

        try:
            parsed_blocks = await self.edit_format.validate(response_text)
        except Exception as e:
            if isinstance(e, NoBlocksFoundError):
                return Command(goto="end_node")

            if isinstance(e, PreFlightCheckError):
                console.print_warning_panel(str(e), title="Parse Error: Pre-flight check failed")

                error_message = list_to_multiline_text(
                    [
                        "Your *Pseudo-XML Edit Blocks* failed pre-flight validation:",
                        "```",
                        str(e),
                        "```",
                        "No changes were applied. Fix the malformed blocks and retry with corrected syntax.",
                        "Reply with ALL *Pseudo-XML Edit Blocks* (corrected and uncorrected) plus any other content from your original message.",
                        runtime.context.recovery_steps or "",
                    ]
                )

                return Command(goto="assistant_node", update={"errors": error_message, "metadata": metadata})

            log.exception(e)
            raise

        # Check for validation errors in parsed blocks
        validation_errors = []
        valid_count = 0

        for block in parsed_blocks:
            if block.block_status != BlockStatus.VALID:
                error_info = f"{block.status_message}\n\n{block.to_search_replace_format()}"
                validation_errors.append(error_info)
            else:
                valid_count += 1

        if validation_errors:
            failed_count = len(validation_errors)
            error_message = "\n\n".join(validation_errors)

            error_message = list_to_multiline_text(
                [
                    f"The following {failed_count} *Pseudo-XML Edit Blocks* failed validation:",
                    error_message,
                    "No changes were applied.",
                    "Reply with ALL *Pseudo-XML Edit Blocks* (corrected and uncorrected) plus any other content from your original message.",
                    runtime.context.recovery_steps or "",
                ]
            )

            console.print_warning_panel(error_message, title="Validation Error")

            return Command(goto="assistant_node", update={"errors": error_message, "metadata": metadata})

        # Once all blocks are valid THEN apply them.
        parsed_blocks = await self.edit_format.apply(parsed_blocks)

        return Command(goto="lint_node", update={"parsed_blocks": parsed_blocks, "metadata": metadata})
