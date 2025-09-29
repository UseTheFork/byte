from langgraph.graph.state import RunnableConfig

from byte.core.utils import extract_content_from_message
from byte.domain.agent.implementations.coder.edit_format.base import (
    BlockStatus,
    EditFormat,
)
from byte.domain.agent.implementations.coder.edit_format.exceptions import (
    PreFlightCheckError,
)
from byte.domain.agent.nodes.base_node import Node
from byte.domain.agent.state import BaseState


class ParseBlocksNode(Node):
    async def boot(self, edit_format: EditFormat, **kwargs):
        self.edit_format = edit_format

    async def __call__(self, state: BaseState, config: RunnableConfig):
        """Parse commands from the last assistant message."""
        messages = state["messages"]
        last_message = messages[-1]

        response_text = extract_content_from_message(last_message)

        try:
            parsed_blocks = await self.edit_format.handle(response_text)
        except Exception as e:
            if isinstance(e, PreFlightCheckError):
                return {
                    "agent_status": "validation_error",
                    "errors": [("user", str(e))],
                }
            raise

        # Check for validation errors in parsed blocks
        validation_errors = []
        valid_count = 0

        for block in parsed_blocks:
            if block.block_status != BlockStatus.VALID:
                error_info = (
                    f"{block.status_message}\n\n{block.to_search_replace_format()}"
                )
                validation_errors.append(error_info)
            else:
                valid_count += 1

        # If there are validation errors, return them
        if validation_errors:
            failed_count = len(validation_errors)
            error_message = f"The following {failed_count} *SEARCH/REPLACE blocks* failed. Check the file content and try again. The other {valid_count} *SEARCH/REPLACE blocks* succeeded.\n\n"
            error_message += "\n\n".join(validation_errors)

            return {
                "agent_status": "validation_error",
                "errors": [("user", error_message)],
            }

        return {"agent_status": "valid", "parsed_blocks": parsed_blocks}
