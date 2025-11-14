from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from byte.domain.agent.implementations.coder.agent import CoderAgent
from byte.domain.agent.nodes.end_node import EndNode
from byte.domain.agent.nodes.show_node import ShowNode
from byte.domain.agent.nodes.start_node import StartNode
from byte.domain.agent.state import BaseState


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

        graph = StateGraph(BaseState)
        graph.add_node("start_node", await self.make(StartNode))
        graph.add_node("show_node", await self.make(ShowNode))
        graph.add_node("end_node", await self.make(EndNode))

        # Define edges
        graph.add_edge(START, "start_node")
        graph.add_edge("start_node", "show_node")
        graph.add_edge("show_node", "end_node")
        graph.add_edge("end_node", END)

        checkpointer = await self.get_checkpointer()
        return graph.compile(checkpointer=checkpointer)
