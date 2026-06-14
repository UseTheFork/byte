from byte.harness import BootstrapInstructionTool, HarnessAgentNode
from byte.node.nodes import EndNode, ToolNode
from byte.orchestration import BaseWorkflow, GraphBuilder, PhaseModel, RoutePhaseModel, UpdatePhaseTool
from byte.skills import CreateSkillTool, SkillCreatorAgentNode
from byte.system import UserConfirmOrInputTool, UserConfirmTool, UserInputTextTool, UserSelectTool


class CreateSkillWorkflow(BaseWorkflow):
    """
    Workflow for creating new skills through intent capture, drafting, and creation.

    Orchestrates a multi-phase graph pipeline that gathers skill requirements,
    generates a draft implementation, and creates the skill artifact using
    available tools. Phases progress through intent capture (phase 1), draft
    generation (phase 2), skill creation (phase 3), and termination (phase 4).
    """

    def get_phases(self, **kwargs) -> list[PhaseModel | RoutePhaseModel]:
        """Return the phases that define the workflow for creating a new skill."""
        return [
            PhaseModel(
                id="create-instruction",
                content="Consider the conversation history and the user's request to provide a clear, concise instruction describing the skill they would like created.",
                executed_by=HarnessAgentNode,
                note=[
                    f"Use the `{BootstrapInstructionTool.name}` to provied a clear instruction on the changes that need to be made by the workflow",
                    "The `Skill Creator Agent` that you bootstrap has no references to conversation history.",
                    f"If the users request is ambiguous or unclear you may use one `{UserInputTextTool.name}`, `{UserConfirmTool.name}`, `{UserSelectTool.name}` to clarify the request. ONLY DO THIS IF YOU HAVE TO.",
                ],
                tools=[
                    BootstrapInstructionTool,
                    UserInputTextTool,
                    UserConfirmTool,
                    UserSelectTool,
                ],
            ),
            PhaseModel(
                id="capture-intent",
                content="Capture intent - understand what the skill should do, when it triggers, and what the expected output looks like.",
                note=[
                    f"Use `{UserSelectTool.name}`, or `{UserConfirmTool.name}` to gather information from the user",
                ],
                tools=[
                    UserInputTextTool,
                    UserConfirmOrInputTool,
                    UserConfirmTool,
                    UserSelectTool,
                ],
                executed_by=SkillCreatorAgentNode,
            ),
            PhaseModel(
                id="generate-draft",
                content=f"Generate a draft of the skill and confirm using the {UserConfirmOrInputTool.name}",
                note=[
                    f"You MUST use the `{UpdatePhaseTool.name}` tool to end complete this phase.",
                ],
                tools=[
                    UserConfirmOrInputTool,
                    UpdatePhaseTool,
                ],
                executed_by=SkillCreatorAgentNode,
            ),
            PhaseModel(
                id="create-skill",
                content="Create the skill - use available tools to create the skill with a clear name, description, and instructions.",
                tools=[
                    CreateSkillTool,
                ],
                executed_by=SkillCreatorAgentNode,
            ),
            RoutePhaseModel(
                id="end",
                executed_by=EndNode,
            ),
        ]

    async def build(self):
        """Compile and return the skill creation workflow graph."""

        graph = self.app.make(GraphBuilder, start_node=HarnessAgentNode)

        graph.add_node(HarnessAgentNode)
        graph.add_node(SkillCreatorAgentNode)
        graph.add_node(ToolNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
