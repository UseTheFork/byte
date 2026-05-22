from byte.files.tools.add_files_tool import AddFilesTool
from byte.files.tools.list_files_tool import ListFilesTool
from byte.git.tools.git_grep_tool import GitGrepTool
from byte.node.nodes import EndNode, ToolNode
from byte.orchestration import (
    BaseWorkflow,
    GraphBuilder,
    PhaseModel,
    RoutePhaseModel,
    UpdatePhaseTool,
    UserConfirmPhaseTool,
)
from byte.skills import SkillSelectAgentNode
from byte.specs import SpecCreatorAgentNode
from byte.specs.tools.create_spec_tool import CreateSpecTool
from byte.system.tools.user_confirm_tool import UserConfirmTool
from byte.system.tools.user_select_tool import UserSelectTool


class CreateSpecWorkflow(BaseWorkflow):
    """ """

    def get_phases(self, **kwargs):
        return [
            PhaseModel(
                id="select-skills",
                content="Identify and load the relevant skills based on the user's task",
                executed_by=SkillSelectAgentNode,
                note=[
                    f"If no skills are relvent complete this phase using the `{UpdatePhaseTool.name}` tool.",
                ],
                tools=[
                    UpdatePhaseTool,
                ],
                tool_choice="any",
            ),
            PhaseModel(
                id="capture-intent",
                content="Capture intent — understand what the spec should cover, what problem it solves, and what the expected outcome looks like.",
                note=[
                    " Check out the current project state first (files, docs, recent commits)",
                    """Assess scope: if the request describes multiple independent subsystems (e.g., "build a platform with chat, file storage, billing, and analytics"), flag this immediately. Don't spend questions refining details of a project that needs to be decomposed first.""",
                ],
                tools=[
                    UserSelectTool,
                    UserConfirmTool,
                    ListFilesTool,
                    AddFilesTool,
                    GitGrepTool,
                ],
                executed_by=SpecCreatorAgentNode,
            ),
            PhaseModel(
                id="clarify",
                content="Ask clarifying questions — one at a time, understand purpose/constraints/success criteria",
                note=[
                    "Prefer multiple choice questions when possible, but open-ended is fine too",
                    "Only one question per message - if a topic needs more exploration, break it into multiple questions",
                    "Focus on understanding: purpose, constraints, success criteria",
                    f"Once you believe you understand what you're building, use the `{UpdatePhaseTool.name}` to complete this phase.",
                ],
                tools=[
                    UserSelectTool,
                    UserConfirmTool,
                    UpdatePhaseTool,
                ],
                executed_by=SpecCreatorAgentNode,
            ),
            PhaseModel(
                id="propose",
                content="Propose 2-3 approaches — with trade-offs and your recommendation",
                note=[
                    "Propose 2-3 different approaches with trade-offs",
                    "Present options conversationally with your recommendation and reasoning",
                    "Lead with your recommended option and explain why",
                    f"Once you believe you understand what you're building, use the `{UpdatePhaseTool.name}` to complete this phase.",
                ],
                tools=[
                    UserSelectTool,
                    UserConfirmTool,
                    UpdatePhaseTool,
                ],
                executed_by=SpecCreatorAgentNode,
            ),
            PhaseModel(
                id="present-design",
                content="Presenting the design",
                note=[
                    "Scale each section to its complexity: a few sentences if straightforward, up to 200-300 words if nuanced",
                    "Ask after each section whether it looks right so far",
                    "Cover: architecture, components, data flow, error handling, testing",
                ],
                tools=[
                    UserConfirmTool,
                    UserConfirmPhaseTool,
                ],
                executed_by=SpecCreatorAgentNode,
            ),
            PhaseModel(
                id="create-spec",
                content="Create the spec — use available tools to create the spec with a clear name, description, and instructions.",
                tools=[
                    CreateSpecTool,
                ],
                executed_by=SpecCreatorAgentNode,
            ),
            RoutePhaseModel(
                id="end",
                executed_by=EndNode,
            ),
        ]

    async def build(self):
        """ """

        graph = self.app.make(GraphBuilder, start_node=SpecCreatorAgentNode)

        # Add nodes
        graph.add_node(SpecCreatorAgentNode)
        graph.add_node(SkillSelectAgentNode)
        graph.add_node(ToolNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
