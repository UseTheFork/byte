from byte.orchestration import GraphBuilder
from byte.subgraph import CoderAgent
from byte.workflow import BaseWorkflow


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
