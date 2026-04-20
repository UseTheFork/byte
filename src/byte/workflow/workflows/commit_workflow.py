from byte.node.agents import CommitAgentNode
from byte.node.nodes import LintNode, ToolNode
from byte.orchestration import GraphBuilder
from byte.workflow import BaseWorkflow


class CommitWorkflow(BaseWorkflow):
    """ """

    async def build(self):
        """ """

        graph = GraphBuilder(self.app, start_node=LintNode)

        # Add nodes
        graph.add_node(LintNode, goto=CommitAgentNode)

        graph.add_node(CommitAgentNode)
        graph.add_node(ToolNode)

        # graph.add_node(
        #     ValidationNode,
        #     goto=EndNode,
        #     validators=[
        #         self.app.make(CommitValidator),
        #     ],
        # )

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
