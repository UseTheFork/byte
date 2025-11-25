from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from byte.domain.agent.implementations.base import Agent
from byte.domain.agent.nodes.end_node import EndNode
from byte.domain.agent.nodes.subprocess_node import SubprocessNode
from byte.domain.agent.state import BaseState


class SubprocessAgent(Agent):
    """
    Usage: Invoked via `!` command in the CLI
    """

    async def build(self) -> CompiledStateGraph:
        """Build and compile the coder agent graph with memory and tools."""

        # Create the state graph
        graph = StateGraph(BaseState)

        # Add nodes
        graph.add_node(
            "subprocess_node",
            await self.make(SubprocessNode),
        )
        graph.add_node("end_node", await self.make(EndNode))

        # Define edges
        graph.add_edge(START, "subprocess_node")
        graph.add_edge("subprocess_node", "end_node")
        graph.add_edge("end_node", END)

        checkpointer = await self.get_checkpointer()
        return graph.compile(checkpointer=checkpointer)

    async def get_assistant_runnable(self) -> None:
        pass
