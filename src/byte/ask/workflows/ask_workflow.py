from byte.ask import AskAgentNode
from byte.node.nodes import EndNode, ToolNode
from byte.orchestration import GraphBuilder
from byte.workflow import BaseWorkflow


class AskWorkflow(BaseWorkflow):
    """ """

    def get_plan(self):
        return None

    async def build(self):
        """ """

        graph = self.app.make(GraphBuilder, start_node=AskAgentNode)

        # Add nodes
        graph.add_node(AskAgentNode, goto=EndNode)
        graph.add_node(ToolNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
