from byte.node.agents import CoderAgentNode
from byte.orchestration import GraphBuilder
from byte.workflow import BaseWorkflow


class CoderWorkflow(BaseWorkflow):
    """ """

    async def build(self):
        """ """

        graph = GraphBuilder(self.app, start_node=CoderAgentNode)

        # Add nodes
        graph.add_node(CoderAgentNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
