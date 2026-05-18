from byte.harness import ExecutorAgentNode, HarnessAgentNode
from byte.node.nodes import ToolNode
from byte.orchestration import BaseWorkflow, GraphBuilder


class AgentHarnessWorkflow(BaseWorkflow):
    """ """

    async def build(self):
        """ """

        graph = self.app.make(GraphBuilder, start_node=HarnessAgentNode)

        # Add nodes
        graph.add_node(HarnessAgentNode, goto=ExecutorAgentNode)
        graph.add_node(ExecutorAgentNode)
        graph.add_node(ToolNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
