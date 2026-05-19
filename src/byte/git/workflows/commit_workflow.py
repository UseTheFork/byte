from byte.git import CommitAgentNode, GitCommitTool
from byte.node.nodes import EndNode
from byte.orchestration import BaseWorkflow, CompleteTurnTool, CreateAnalysisTool, GraphBuilder, PhaseModel
from byte.orchestration.models.route_phase_model import RoutePhaseModel


class CommitWorkflow(BaseWorkflow):
    """ """

    def get_phases(self):
        return [
            PhaseModel(
                id="1",
                content="Start with a SHORT analysis of the changes in list format. ",
                note=[
                    f"   - DO NOT include `observations` when using the `{CreateAnalysisTool.name}` tool.",
                ],
                executed_by=CommitAgentNode,
                tools=[
                    CreateAnalysisTool,
                ],
            ),
            PhaseModel(
                id="2",
                content=f"Use the `{GitCommitTool.name}` tool EXACTLY ONE TIME.",
                tools=[
                    GitCommitTool,
                ],
                executed_by=CommitAgentNode,
            ),
            PhaseModel(
                id="3",
                content="Complete the turn with a short summary of the work done during this turn. DO NOT include `key_points`",
                tools=[
                    CompleteTurnTool,
                ],
                executed_by=CommitAgentNode,
            ),
            RoutePhaseModel(
                id="4",
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
