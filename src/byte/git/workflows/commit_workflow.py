from byte.git import CommitAgentNode, GitCommitTool
from byte.node.nodes import EndNode
from byte.orchestration import (
    BaseWorkflow,
    CreateAnalysisTool,
    GraphBuilder,
    PhaseModel,
    RoutePhaseModel,
)


class CommitWorkflow(BaseWorkflow):
    """ """

    def get_phases(self):
        return [
            PhaseModel(
                id="analysis",
                content="Start with a SHORT analysis of the changes in a list format.",
                note=[
                    f"  - DO NOT include `observations` when using the `{CreateAnalysisTool.name}` tool.",
                ],
                executed_by=CommitAgentNode,
                tools=[
                    CreateAnalysisTool,
                ],
            ),
            PhaseModel(
                id="commit",
                content="Create the commit.",
                note=[
                    f"  - Use the `{GitCommitTool.name}` tool EXACTLY ONE TIME.",
                ],
                tools=[
                    GitCommitTool,
                ],
                executed_by=CommitAgentNode,
            ),
            RoutePhaseModel(
                id="end",
                executed_by=EndNode,
            ),
        ]

    async def build(self):
        """ """

        graph = self.app.make(GraphBuilder, start_node=CommitAgentNode)

        # Add nodes
        graph.add_node(CommitAgentNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
