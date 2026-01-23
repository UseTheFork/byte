from langgraph.graph.state import CompiledStateGraph

from byte.agent.implementations.base import Agent
from byte.agent.nodes.subprocess_node import SubprocessNode
from byte.agent.schemas import AssistantContextSchema
from byte.agent.utils.graph_builder import GraphBuilder


class SubprocessAgent(Agent):
    """
    Usage: Invoked via `!` command in the CLI
    """

    async def build(self) -> CompiledStateGraph:
        """Build and compile the coder agent graph with memory and tools."""

        graph = GraphBuilder(self.app, SubprocessNode)
        graph.add_node(SubprocessNode)

        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)

    async def get_assistant_runnable(self) -> AssistantContextSchema:
        return AssistantContextSchema(
            mode="none",
            prompt=None,
            main=None,
            weak=None,
            agent=self.__class__.__name__,
        )
