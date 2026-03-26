from byte.agent import CoderAgent
from byte.agent.utils.graph_builder import GraphBuilder
from byte.workflow import BaseWorkflow

# AI: add doc blocks here ai!


class CoderWorkflow(BaseWorkflow):
    """ """

    async def build(self):
        """ """

        graph = GraphBuilder(self.app, start_node=CoderAgent)

        # Add nodes
        graph.add_node(CoderAgent)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
