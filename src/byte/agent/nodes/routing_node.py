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
            "assistant_node",
            "ask_agent_node",
            "code_reviewer_agent_node",
            "end_node",
            "parse_blocks_node",
            "tool_node",
            "validation_node",
        ]
    ]:
        return Command(
            goto=state.get("node_to"),
        )
