from byte.harness import HarnessAgentNode
from byte.node.nodes import ToolNode
from byte.orchestration import BaseWorkflow, GraphBuilder


class AgentHarnessWorkflow(BaseWorkflow):
    """ """

    async def build(self):
        """ """

        graph = self.app.make(GraphBuilder, start_node=HarnessAgentNode)

        # Add nodes
        graph.add_node(HarnessAgentNode)
        graph.add_node(ToolNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
