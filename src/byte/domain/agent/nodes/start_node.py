from typing import Optional

from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime

from byte.domain.agent.nodes.base_node import Node
from byte.domain.agent.schemas import AssistantContextSchema
from byte.domain.agent.state import BaseState
from byte.domain.prompt_format.service.edit_format_service import EditFormatService


class StartNode(Node):
    async def boot(
        self,
        edit_format: Optional[EditFormatService] = None,
        **kwargs,
    ):
        self.edit_format = edit_format

    async def __call__(self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]):
        result = {
            "agent": runtime.context.agent,
            "edit_format_system": "",
            "masked_messages": [],
            "examples": [],
            "donts": [],
            "errors": None,
        }

        if self.edit_format is not None:
            result["edit_format_system"] = self.edit_format.prompts.system
            result["examples"] = self.edit_format.prompts.examples

        return result
