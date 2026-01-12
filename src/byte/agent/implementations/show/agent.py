from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from byte.agent.implementations.coder.agent import CoderAgent
from byte.agent.nodes.end_node import EndNode
from byte.agent.nodes.show_node import ShowNode
from byte.agent.nodes.start_node import StartNode
from byte.agent.state import BaseState


class ShowAgent(CoderAgent):
    """Agent for displaying conversation history and context.

    Extends CoderAgent to provide a simplified graph that shows the current
    conversation state without executing any AI operations or modifications.
    Usage: `agent = await container.make(ShowAgent); await agent.execute(request)`
    """

    async def build(self) -> CompiledStateGraph:
        """Build and compile the show agent graph with memory.

        Creates a minimal graph that displays conversation history through
        the show node without invoking the assistant or making changes.

        Returns:
            CompiledStateGraph ready for displaying conversation state

        Usage: `graph = await agent.build()` -> returns compiled graph
        """

        graph = StateGraph(BaseState)  # ty:ignore[invalid-argument-type]
        graph.add_node("start_node", self.app.make(StartNode))  # ty:ignore[invalid-argument-type]
        graph.add_node("show_node", self.app.make(ShowNode))  # ty:ignore[invalid-argument-type]
        graph.add_node("end_node", self.app.make(EndNode))  # ty:ignore[invalid-argument-type]

        # Define edges
        graph.add_edge(START, "start_node")

        checkpointer = await self.get_checkpointer()
        return graph.compile(checkpointer=checkpointer)
