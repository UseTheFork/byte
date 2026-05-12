from byte.constitution import ConstitutionAgentNode
from byte.node.nodes import ToolNode
from byte.orchestration import GraphBuilder
from byte.workflow import BaseWorkflow


class ConstitutionWorkflow(BaseWorkflow):
    """ """

    async def build(self):
        """ """

        graph = self.app.make(GraphBuilder, start_node=ConstitutionAgentNode)

        # Add nodes
        graph.add_node(ConstitutionAgentNode)
        graph.add_node(ToolNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
