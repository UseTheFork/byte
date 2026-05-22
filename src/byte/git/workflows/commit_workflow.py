from byte.git import CommitAgentNode, GitCommitTool
from byte.node.nodes import EndNode
from byte.orchestration import (
    BaseWorkflow,
    CreateAnalysisTool,
    GraphBuilder,
    PhaseModel,
    RoutePhaseModel,
)
from byte.support import Section, SectionType


class CommitWorkflow(BaseWorkflow):
    """ """

    def get_phases(self):
        return [
            PhaseModel(
                id="analysis",
                content=f"Review the provided context and diffs which are about to be committed to a git repo. Create a SHORT list of the changes and pass them to the `{CreateAnalysisTool.name}(observations).",
                note=[
                    "Review the diffs carefully.",
                    f"DO NOT include `summary` when using the `{CreateAnalysisTool.name}` tool.",
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
                    f"Use the `{GitCommitTool.name}` tool EXACTLY ONE TIME.",
                    f"You **MUST** follow the commit guidelines provided in the {Section.ref(SectionType.RULES)}.",
                    "Read and apply ALL rules for commit types, scopes, and description formatting.",
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
