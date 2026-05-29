from byte.files.tools.add_files_tool import AddFilesTool
from byte.files.tools.list_files_tool import ListFilesTool
from byte.git.tools.git_grep_tool import GitGrepTool
from byte.harness import BootstrapSkillsFilesTool, HarnessAgentNode
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
from byte.system.tools.user_confirm_tool import UserConfirmTool
from byte.system.tools.user_select_tool import UserSelectTool


class CreateRefractorWorkflow(BaseWorkflow):
    """ """

    def get_phases(self, **kwargs):
        return [
            PhaseModel(
                id="select-skills",
                content="Identify and load the relevant skills based on the user's task",
                executed_by=HarnessAgentNode,
                tools=[
                    BootstrapSkillsFilesTool,
                ],
                tool_choice="any",
            ),
            PhaseModel(
                id="analyze",
                content="Analyze - review the loaded files/domain and provide recommendations on what should be refactored and how.",
                note=[
                    "Analyze code for refactoring opportunities: duplication, complexity, naming, structure, architectural patterns, error handling",
                    "Present findings conversationally with specific examples from the analyzed code",
                    "Focus on understanding the current state and identifying high-impact refactoring opportunities",
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
                content="Ask clarifying questions - one at a time, understand which refactoring recommendations to pursue, scope, and priorities",
                note=[
                    "Prefer multiple choice questions when possible, but open-ended is fine too",
                    "Only one question per message - if a topic needs more exploration, break it into multiple questions",
                    "Focus on understanding: which refactoring recommendations the user wants to pursue, scope, priorities, and constraints",
                    f"Once you believe you understand the refactoring plan, use the `{UpdatePhaseTool.name}` to complete this phase.",
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
                content="Propose 2-3 refactoring approaches - with trade-offs and your recommendation",
                note=[
                    "Propose 2-3 different refactoring approaches with trade-offs",
                    "Present options conversationally with your recommendation and reasoning",
                    "Lead with your recommended option and explain why",
                    f"Once you believe you have the refactoring plan agreed upon, use the `{UpdatePhaseTool.name}` to complete this phase.",
                ],
                tools=[
                    UserSelectTool,
                    UserConfirmTool,
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
        """ """

        graph = self.app.make(GraphBuilder, start_node=HarnessAgentNode)

        # Add nodes
        graph.add_node(SpecCreatorAgentNode)
        graph.add_node(HarnessAgentNode)
        graph.add_node(ToolNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
