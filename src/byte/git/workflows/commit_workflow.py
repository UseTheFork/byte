from byte.git import CommitAgentNode, GitCommitTool
from byte.node.nodes import LintNode, ToolNode
from byte.orchestration import BaseWorkflow, CompleteTurnTool, CreateAnalysisTool, GraphBuilder, PhaseModel


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
                agent=CommitAgentNode,
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
                agent=CommitAgentNode,
            ),
            PhaseModel(
                id="3",
                content="Complete the turn with a short summary of the work done during this turn. DO NOT include `key_points`",
                tools=[
                    CompleteTurnTool,
                ],
            ),
        ]

    async def build(self):
        """ """

        graph = self.app.make(GraphBuilder, start_node=LintNode)

        # Add nodes
        graph.add_node(LintNode, goto=CommitAgentNode)
        graph.add_node(ToolNode)
        graph.add_node(CommitAgentNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
