from byte.git import CommitAgentNode, GitCommitTool
from byte.node.nodes import LintNode, ToolNode
from byte.orchestration import BaseWorkflow, CreateAnalysisTool, GraphBuilder, PhaseModel


class CommitWorkflow(BaseWorkflow):
    """ """

    def get_phases(self):
        return [
            PhaseModel(
                id="1",
                content="Start with a SHORT analysis of the changes in list format.",
                agent=CommitAgentNode,
                tools=[
                    CreateAnalysisTool,
                ],
            ),
            PhaseModel(
                id="2",
                content=f"Use the `{GitCommitTool.name}` tool.",
                note=[
                    f"   - The `{GitCommitTool.name}` only becomes available once the first phase is completed.",
                ],
                tools=[
                    GitCommitTool,
                ],
                agent=CommitAgentNode,
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
