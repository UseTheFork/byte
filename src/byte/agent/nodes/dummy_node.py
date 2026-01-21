from typing import Literal

from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.agent import AssistantContextSchema, BaseState, DummyNodeReachedException, Node


class DummyNode(Node):
    async def __call__(
        self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]
    ) -> Command[Literal["assistant_node"]]:
        raise DummyNodeReachedException(
            "Reached dummy node during execution. This indicates a routing error in the agent graph."
        )
