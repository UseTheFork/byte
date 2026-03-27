from byte.node import LintNode
from byte.orchestration import GraphBuilder
from byte.subgraph import CoderAgent, CommitAgent
from byte.workflow import BaseWorkflow


class CommitWorkflow(BaseWorkflow):
    """ """

    async def build(self):
        """ """

        graph = GraphBuilder(self.app, start_node=LintNode)

        # Add nodes
        graph.add_node(LintNode, goto=CommitAgent)

        graph.add_node(CommitAgent)
        graph.add_node(CoderAgent)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
