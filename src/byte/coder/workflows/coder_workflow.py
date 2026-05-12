from byte.coder import CoderAgentNode
from byte.node.nodes import LintNode, ToolNode
from byte.orchestration import GraphBuilder
from byte.workflow import BaseWorkflow


class CoderWorkflow(BaseWorkflow):
    """ """

    async def build(self):
        """ """

        graph = self.app.make(GraphBuilder, start_node=CoderAgentNode)

        # Add nodes
        graph.add_node(CoderAgentNode, goto=LintNode)
        graph.add_node(ToolNode)
        graph.add_node(LintNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
