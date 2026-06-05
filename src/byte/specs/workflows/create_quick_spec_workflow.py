from byte.harness import BootstrapInstructionTool, HarnessAgentNode
from byte.node.nodes import EndNode, ToolNode
from byte.orchestration import (
    BaseWorkflow,
    GraphBuilder,
    PhaseModel,
    RoutePhaseModel,
    UpdatePhaseTool,
)
from byte.specs import CreateTaskTool, SpecCreatorAgentNode, SpecTaskCreatorAgentNode
from byte.specs.tools.create_spec_tool import CreateSpecTool
from byte.system import UserConfirmOrInputTool, UserConfirmTool, UserInputTextTool, UserSelectTool


class CreateQuickSpecWorkflow(BaseWorkflow):
    """Quick spec workflow without the analyze phase."""

    def get_phases(self, **kwargs):
        return [
            PhaseModel(
                id="create-instruction",
                content="Consider the conversation history and the user's request to provide a clear, concise instruction describing the changes that should be made.",
                executed_by=HarnessAgentNode,
                note=[
                    f"Use the `{BootstrapInstructionTool.name}` to provide a clear instruction on the changes that need to be made by the workflow",
                    "The `Spec Creator Agent` that you bootstrap has no references to conversation history.",
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
                id="clarify",
                content="If the task is unclear, ask clarifying questions — one at a time, to understand which recommendations to pursue, scope, and priorities. If the task is already clear, skip directly to completing this phase.",
                note=[
                    "If the instruction is already clear and unambiguous, you may skip questions entirely and use the `UpdatePhaseTool.name` to complete this phase immediately.",
                    "Prefer multiple choice questions when possible, but open-ended is fine too",
                    "Only one question per message - if a topic needs more exploration, break it into multiple questions",
                    "Focus on understanding: which recommendations the user wants to pursue, scope, priorities, and constraints",
                    f"Once you believe you understand the plan, use the `{UpdatePhaseTool.name}` to complete this phase.",
                ],
                tools=[
                    UserSelectTool,
                    UserConfirmTool,
                    UserConfirmOrInputTool,
                    UpdatePhaseTool,
                ],
                executed_by=SpecCreatorAgentNode,
            ),
            PhaseModel(
                id="create-spec",
                content="Create the spec - use available tools to create the spec with a clear name, description, and instructions.",
                tools=[
                    CreateSpecTool,
                ],
                executed_by=SpecCreatorAgentNode,
            ),
            PhaseModel(
                id="create-tasks",
                content="Create the tasks - use available tools to create the tasks.",
                tools=[
                    CreateTaskTool,
                ],
                executed_by=SpecTaskCreatorAgentNode,
            ),
            RoutePhaseModel(
                id="end",
                executed_by=EndNode,
            ),
        ]

    async def build(self):
        """Build the workflow graph."""

        graph = self.app.make(GraphBuilder, start_node=HarnessAgentNode)

        # Add nodes
        graph.add_node(HarnessAgentNode)
        graph.add_node(SpecCreatorAgentNode)
        graph.add_node(SpecTaskCreatorAgentNode)
        graph.add_node(ToolNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
