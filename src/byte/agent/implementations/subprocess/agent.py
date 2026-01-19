from langgraph.graph.state import CompiledStateGraph

from byte.agent.implementations.base import Agent
from byte.agent.nodes.subprocess_node import SubprocessNode
from byte.agent.schemas import AssistantContextSchema


class SubprocessAgent(Agent):
    """
    Usage: Invoked via `!` command in the CLI
    """

    async def build(self) -> CompiledStateGraph:
        """Build and compile the coder agent graph with memory and tools."""

        graph = self.get_base_graph(
            [
                "parse_blocks_node",
                "extract_node",
                "validation_node",
                "assistant_node",
            ],
            "subprocess_node",
        )

        # Add nodes
        graph.add_node(
            "subprocess_node",
            self.app.make(SubprocessNode),  # ty:ignore[invalid-argument-type]
        )

        checkpointer = await self.get_checkpointer()
        return graph.compile(checkpointer=checkpointer)

    async def get_assistant_runnable(self) -> AssistantContextSchema:
        return AssistantContextSchema(
            mode="none",
            prompt=None,
            main=None,
            weak=None,
            agent=self.__class__.__name__,
        )
