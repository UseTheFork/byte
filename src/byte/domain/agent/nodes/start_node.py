from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime

from byte.domain.agent.nodes.base_node import Node
from byte.domain.agent.schemas import AssistantContextSchema, MetadataSchema
from byte.domain.agent.state import BaseState
from byte.domain.prompt_format.service.edit_format_service import EditFormatService


class StartNode(Node):
    async def __call__(self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]):
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
