from byte.coder import CoderAgentNode
from byte.files import (
    DeleteFileTool,
    EditFileTool,
    ReplaceFileTool,
    WriteFileTool,
)
from byte.node.nodes import LintNode, ToolNode
from byte.orchestration import BaseWorkflow, CompleteTurnTool, CreatePlanTool, GraphBuilder, PhaseModel


class CoderWorkflow(BaseWorkflow):
    """ """

    def get_phases(self):
        return [
            PhaseModel(
                id="1",
                content="Create a clear, step-by-step plan for implementing the requested changes.",
                agent=CoderAgentNode,
                tools=[
                    CreatePlanTool,
                ],
            ),
            PhaseModel(
                id="2",
                content="Use available tools to apply the changes to complete the step-by-step plan",
                tools=[
                    EditFileTool,
                    WriteFileTool,
                    DeleteFileTool,
                    ReplaceFileTool,
                ],
                agent=CoderAgentNode,
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

        graph = self.app.make(GraphBuilder, start_node=CoderAgentNode)

        # Add nodes
        graph.add_node(CoderAgentNode, goto=LintNode)
        graph.add_node(ToolNode)
        graph.add_node(LintNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
