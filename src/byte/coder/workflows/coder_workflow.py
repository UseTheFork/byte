from byte.coder import CoderAgentNode
from byte.files import (
    DeleteFileTool,
    EditFileTool,
    ReplaceFileTool,
    WriteFileTool,
)
from byte.lint.tools.lint_tool import LintTool
from byte.node.nodes import EndNode, ToolNode
from byte.orchestration import (
    BaseWorkflow,
    CompleteTurnTool,
    CreatePlanTool,
    GraphBuilder,
    PhaseModel,
    RoutePhaseModel,
    UpdatePhaseTool,
)


class CoderWorkflow(BaseWorkflow):
    """
    Primary workflow for AI-driven code changes.

    Orchestrates a multi-phase graph pipeline that plans, implements, lints,
    and summarises code modifications requested by the user. Phases progress
    through planning (phase 1), file editing (phase 2), lint routing (phase 3),
    and turn completion (phase 4), terminating at an end node (phase 5).
    """

    def get_phases(self):
        return [
            PhaseModel(
                id="1",
                content="Create a clear, step-by-step plan for implementing the requested changes.",
                executed_by=CoderAgentNode,
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
                executed_by=CoderAgentNode,
            ),
            PhaseModel(
                id="3",
                content=f"Run the `{LintTool.name}` tool on all touched files. If lint errors are reported, fix them using the available file tools and re-run the lint tool. Repeat until linting passes with no errors.",
                tools=[
                    LintTool,
                    EditFileTool,
                    WriteFileTool,
                    DeleteFileTool,
                    ReplaceFileTool,
                    UpdatePhaseTool,
                ],
                note=[
                    f"   - To Complete this phase use the `{UpdatePhaseTool.name}` tool.",
                ],
                executed_by=CoderAgentNode,
            ),
            PhaseModel(
                id="4",
                content="Complete the turn with a short summary of the work done during this turn. DO NOT include `key_points`",
                tools=[
                    CompleteTurnTool,
                ],
                executed_by=CoderAgentNode,
            ),
            RoutePhaseModel(
                id="5",
                executed_by=EndNode,
            ),
        ]

    async def build(self):
        """ """

        graph = self.app.make(GraphBuilder, start_node=CoderAgentNode)

        # Add nodes
        graph.add_node(CoderAgentNode)
        graph.add_node(ToolNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
