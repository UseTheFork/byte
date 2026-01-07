from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from byte.agent.implementations.base import Agent
from byte.agent.nodes.end_node import EndNode
from byte.agent.nodes.subprocess_node import SubprocessNode
from byte.agent.schemas import AssistantContextSchema
from byte.agent.state import BaseState


class SubprocessAgent(Agent):
    """
    Usage: Invoked via `!` command in the CLI
    """

    async def build(self) -> CompiledStateGraph:
        """Build and compile the coder agent graph with memory and tools."""

        # Create the state graph
        graph = StateGraph(BaseState, context_schema=AssistantContextSchema)

        # Add nodes
        graph.add_node(
            "subprocess_node",
            self.make(SubprocessNode),
        )
        graph.add_node("end_node", self.make(EndNode))

        # Define edges
        graph.add_edge(START, "subprocess_node")
        graph.add_edge("subprocess_node", "end_node")
        graph.add_edge("end_node", END)

        checkpointer = await self.get_checkpointer()
        return graph.compile(checkpointer=checkpointer)

    async def get_assistant_runnable(self) -> None:
        pass
