from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from byte.domain.agent.implementations.base import Agent
from byte.domain.agent.nodes.copy_node import CopyNode
from byte.domain.agent.nodes.end_node import EndNode
from byte.domain.agent.state import BaseState


class CopyAgent(Agent):
    """Agent for extracting and copying code blocks from messages.

    Provides an interactive workflow to select and copy code blocks from
    the last AI response to the system clipboard using pyperclip.
    Usage: Invoked via `/copy` command in the CLI
    """

    async def build(self) -> CompiledStateGraph:
        """Build and compile the coder agent graph with memory and tools."""

        graph = StateGraph(BaseState)
        graph.add_node("copy_node", await self.make(CopyNode))
        graph.add_node("end_node", await self.make(EndNode))

        # Define edges
        graph.add_edge(START, "copy_node")
        graph.add_edge("end_node", END)

        checkpointer = await self.get_checkpointer()
        return graph.compile(checkpointer=checkpointer, debug=False)

    async def get_assistant_runnable(self) -> None:
        pass
