from byte.node.agents import CoderAgentNode
from byte.node.nodes import LintNode, ParseBlocksNode
from byte.orchestration import GraphBuilder
from byte.workflow import BaseWorkflow


class CoderWorkflow(BaseWorkflow):
    """ """

    async def build(self):
        """ """

        graph = GraphBuilder(self.app, start_node=CoderAgentNode)

        # Add nodes
        graph.add_node(CoderAgentNode, goto=ParseBlocksNode)
        graph.add_node(ParseBlocksNode)
        graph.add_node(LintNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
