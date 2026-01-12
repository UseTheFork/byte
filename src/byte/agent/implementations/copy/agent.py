from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from byte.agent import Agent, BaseState, CopyNode, EndNode


class CopyAgent(Agent):
    """Agent for extracting and copying code blocks from messages.

    Provides an interactive workflow to select and copy code blocks from
    the last AI response to the system clipboard using pyperclip.
    Usage: Invoked via `/copy` command in the CLI
    """

    async def build(self) -> CompiledStateGraph:
        """Build and compile the coder agent graph with memory and tools."""

        graph = StateGraph(BaseState)  # ty:ignore[invalid-argument-type]
        graph.add_node("copy_node", self.app.make(CopyNode))  # ty:ignore[invalid-argument-type]
        graph.add_node("end_node", self.app.make(EndNode))  # ty:ignore[invalid-argument-type]

        # Define edges
        graph.add_edge(START, "copy_node")

        checkpointer = await self.get_checkpointer()
        return graph.compile(checkpointer=checkpointer)

    async def get_assistant_runnable(self) -> None:
        pass
