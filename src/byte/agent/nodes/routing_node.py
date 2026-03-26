from typing import Literal

from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.agent import AssistantContextSchema, BaseState, Node


# THis is here to control the below Literal and be able to have all possible nodes in one place.
class RoutingNode(Node):
    async def __call__(
        self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]
    ) -> Command[
        Literal[
            "weak_model_node",
            "reasoning_model_node",
            "main_model_node",
            "lint_node",
            "ask_agent",
            "end_node",
            "parse_blocks_node",
            "tool_node",
            "validation_node",
            "coder_agent",
        ]
    ]:
        routing = state.get("routing", {})
        self.app["log"].info(f"Routing >> From: {routing.get('source')} >> To: {routing.get('target')}")

        return Command(
            goto=routing.get("target"),
        )
