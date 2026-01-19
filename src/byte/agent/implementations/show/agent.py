from langgraph.graph.state import CompiledStateGraph

from byte.agent.implementations.coder.agent import CoderAgent
from byte.agent.nodes.show_node import ShowNode


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

        graph = self.get_base_graph(
            [
                "parse_blocks_node",
            ],
        )

        graph.add_node("show_node", self.app.make(ShowNode))  # ty:ignore[invalid-argument-type]

        checkpointer = await self.get_checkpointer()
        return graph.compile(checkpointer=checkpointer)
