from byte.documentation import DocumentationAgentNode
from byte.files import (
    DeleteFileTool,
    EditFileTool,
    ReplaceFileTool,
    WriteFileTool,
)
from byte.harness import BootstrapAgentTool, HarnessAgentNode
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
from byte.system import UserConfirmTool, UserInputTextTool, UserSelectTool


class DocumentationWorkflow(BaseWorkflow):
    """
    Primary workflow for AI-driven documentation changes.

    Orchestrates a multi-phase graph pipeline that plans, implements, lints,
    and summarises documentation modifications requested by the user. Phases progress
    through planning (phase 1), file editing (phase 2), lint routing (phase 3),
    and turn completion (phase 4), terminating at an end node (phase 5).
    """

    def get_phases(self, **kwargs):

        return [
            PhaseModel(
                id="select-skills-and-files",
                content="Identify and load the relevant skills, reference files, and files that will need to be edited based on the user's task. Then use the conversation history and the users request to create a short, clear, concise instruction to pass to the documentation agent.",
                executed_by=HarnessAgentNode,
                note=[
                    f"Use the `{BootstrapAgentTool.name}` to load skills, editable files, reference files, and provied a clear instruction on the changes that need to be made by the workflow",
                    "The documentation agent that you bootstrap has no references to conversation history.",
                    f"If the users request is ambiguous or unclear you may use one `{UserInputTextTool.name}`, `{UserConfirmTool.name}`, `{UserSelectTool.name}` to clarify the request. ONLY DO THIS IF YOU HAVE TO.",
                ],
                tools=[
                    BootstrapAgentTool,
                    UserInputTextTool,
                    UserConfirmTool,
                    UserSelectTool,
                ],
            ),
            PhaseModel(
                id="create-plan",
                content="Create a clear, step-by-step plan for implementing the requested changes.",
                executed_by=DocumentationAgentNode,
                tools=[
                    CreatePlanTool,
                ],
            ),
            PhaseModel(
                id="apply-changes",
                content="Use available tools to apply the changes to complete the step-by-step plan",
                tools=[
                    EditFileTool,
                    WriteFileTool,
                    DeleteFileTool,
                    ReplaceFileTool,
                    UpdatePhaseTool,
                ],
                note=[
                    f"To Complete this phase you may use the `{UpdatePhaseTool.name}` tool or one of the provided file tools.",
                ],
                executed_by=DocumentationAgentNode,
            ),
            PhaseModel(
                id="linting",
                content=f"Run the `{LintTool.name}` tool FIRST. If lint errors are reported, fix them using the available file tools and re-run the lint tool. Repeat until linting passes with no errors.",
                tools=[
                    LintTool,
                    EditFileTool,
                    WriteFileTool,
                    DeleteFileTool,
                    ReplaceFileTool,
                    UpdatePhaseTool,
                ],
                note=[
                    f"To Complete this phase use the `{UpdatePhaseTool.name}` tool.",
                ],
                executed_by=DocumentationAgentNode,
            ),
            PhaseModel(
                id="summary",
                content="Complete the turn with a short summary of the work done during this turn.",
                note=[
                    "Only include 2-3 `key_points`",
                ],
                tools=[
                    CompleteTurnTool,
                ],
                executed_by=DocumentationAgentNode,
            ),
            RoutePhaseModel(
                id="end",
                executed_by=EndNode,
            ),
        ]

    async def build(self):
        """Compile the documentation workflow graph and return the executable workflow."""

        graph = self.app.make(GraphBuilder, start_node=HarnessAgentNode)

        # Add nodes
        graph.add_node(HarnessAgentNode)
        graph.add_node(DocumentationAgentNode)
        graph.add_node(ToolNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
