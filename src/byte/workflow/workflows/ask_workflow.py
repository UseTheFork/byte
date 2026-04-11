from byte.node.agents import AskAgentNode
from byte.node.nodes import EndNode
from byte.orchestration import GraphBuilder
from byte.workflow import BaseWorkflow


class AskWorkflow(BaseWorkflow):
    """ """

    async def build(self):
        """ """

        graph = GraphBuilder(self.app, start_node=AskAgentNode)

        # Add nodes
        graph.add_node(AskAgentNode, goto=EndNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
