from langgraph.graph.state import CompiledStateGraph

from byte.agent import Agent, CopyNode
from byte.agent.utils.graph_builder import GraphBuilder


class CopyAgent(Agent):
    """Agent for extracting and copying code blocks from messages.

    Provides an interactive workflow to select and copy code blocks from
    the last AI response to the system clipboard using pyperclip.
    Usage: Invoked via `/copy` command in the CLI
    """

    async def build(self) -> CompiledStateGraph:
        """Build and compile the coder agent graph with memory and tools."""

        graph = GraphBuilder(self.app)
        graph.add_node(CopyNode)

        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)

    async def get_assistant_runnable(self) -> None:
        pass
