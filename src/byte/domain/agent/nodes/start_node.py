from typing import Optional

from langgraph.graph.state import RunnableConfig

from byte.domain.agent.nodes.base_node import Node
from byte.domain.agent.state import BaseState
from byte.domain.edit_format.service.edit_format_service import EditFormatService


class StartNode(Node):
    async def boot(
        self,
        agent: str,
        edit_format: Optional[EditFormatService] = None,
        **kwargs,
    ):
        self.edit_format = edit_format
        self.agent = agent

    async def __call__(self, state: BaseState, config: RunnableConfig):
        result = {
            "agent": self.agent,
            "agent_status": "",
            "edit_format_system": "",
            "errors": [],
            "examples": [],
        }

        if self.edit_format is not None:
            result["edit_format_system"] = self.edit_format.prompts.system
            result["examples"] = self.edit_format.prompts.examples

        return result
