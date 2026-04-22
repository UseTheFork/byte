from typing import Literal

from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.node import BaseNode
from byte.orchestration import AssistantContextSchema, BaseState


# This is here to control the below Literal and be able to have all possible nodes in one place.
class RoutingNode(BaseNode):
    async def __call__(
        self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]
    ) -> Command[
        Literal[
            "lint_node",
            "end_node",
            "tool_node",
            "validation_node",
            "commit_agent_node",
            "coder_agent_node",
            # "coder_plan_agent_node",
            "ask_agent_node",
        ]
    ]:
        routing = state.get("routing", {})
        self.app["log"].info(f"Routing >> From: {routing.get('source')} >> To: {routing.get('target')}")

        return Command(goto=routing.get("target"))  # ty:ignore[invalid-return-type]
