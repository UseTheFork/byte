from byte.node.agents import CoderAgentNode, CoderPlanAgentNode
from byte.node.nodes import LintNode, ToolNode
from byte.orchestration import GraphBuilder
from byte.workflow import BaseWorkflow


class CoderWorkflow(BaseWorkflow):
    """ """

    async def build(self):
        """ """

        graph = GraphBuilder(self.app, start_node=CoderPlanAgentNode)

        # Add nodes
        graph.add_node(CoderPlanAgentNode, goto=CoderAgentNode)
        graph.add_node(CoderAgentNode, goto=LintNode)
        graph.add_node(ToolNode)
        graph.add_node(LintNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
