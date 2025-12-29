from typing import Any

from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime

from byte.domain.agent import AssistantContextSchema, BaseState, MetadataSchema, Node
from byte.domain.prompt_format import EditFormatService


class StartNode(Node):
    async def __call__(
        self,
        state: BaseState,
        *,
        runtime: Runtime[AssistantContextSchema],
        config: RunnableConfig,
    ) -> Any:
        edit_format = await self.make(EditFormatService)

        result = {
            "agent": runtime.context.agent,
            "edit_format_system": edit_format.prompts.system,
            "masked_messages": [],
            "examples": edit_format.prompts.examples,
            "donts": [],
            "errors": None,
            "metadata": MetadataSchema(iteration=0),
        }

        return result
