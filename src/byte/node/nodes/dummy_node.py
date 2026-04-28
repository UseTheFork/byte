from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.node import BaseNode
from byte.orchestration import AssistantContextSchema, BaseState, DummyNodeReachedException


class DummyNode(BaseNode):
    async def __call__(
        self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]
    ) -> Command[str]:
        raise DummyNodeReachedException(
            "Reached dummy node during execution. This indicates a routing error in the agent graph."
        )
