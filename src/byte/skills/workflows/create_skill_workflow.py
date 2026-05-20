from byte.files.tools.add_files_tool import AddFilesTool
from byte.files.tools.list_files_tool import ListFilesTool
from byte.git.tools.git_grep_tool import GitGrepTool
from byte.node.nodes import EndNode, ToolNode
from byte.orchestration import BaseWorkflow, GraphBuilder, PhaseModel, RoutePhaseModel, UpdatePhaseTool
from byte.skills import SkillCreatorAgentNode
from byte.skills.tools.create_skill_tool import CreateSkillTool
from byte.system import UserConfirmOrInputTool
from byte.system.tools.user_confirm_tool import UserConfirmTool
from byte.system.tools.user_select_tool import UserSelectTool


class CreateSkillWorkflow(BaseWorkflow):
    """ """

    def get_phases(self):
        return [
            PhaseModel(
                id="1",
                content="Capture intent — understand what the skill should do, when it triggers, and what the expected output looks like.",
                note=[
                    f"   - Use `{UserSelectTool.name}`, or `{UserConfirmTool.name}` to gather information from the user",
                    f"   - Use `{ListFilesTool.name}`, `{AddFilesTool.name}`, or `{GitGrepTool.name}` to gather additional context if needed",
                ],
                tools=[
                    UserSelectTool,
                    UserConfirmTool,
                    ListFilesTool,
                    AddFilesTool,
                    GitGrepTool,
                ],
                executed_by=SkillCreatorAgentNode,
            ),
            PhaseModel(
                id="2",
                content=f"Generate a draft of the skill and confirm using the {UserConfirmOrInputTool.name}",
                note=[
                    f"   - You MUST use the `{UpdatePhaseTool.name}` tool to end complete this phase.",
                ],
                tools=[
                    UserConfirmOrInputTool,
                    UpdatePhaseTool,
                ],
                executed_by=SkillCreatorAgentNode,
            ),
            PhaseModel(
                id="3",
                content="Create the skill — use available tools to create the skill with a clear name, description, and instructions.",
                tools=[
                    CreateSkillTool,
                ],
                executed_by=SkillCreatorAgentNode,
            ),
            RoutePhaseModel(
                id="4",
                executed_by=EndNode,
            ),
        ]

    async def build(self):
        """ """

        graph = self.app.make(GraphBuilder, start_node=SkillCreatorAgentNode)

        # Add nodes
        graph.add_node(SkillCreatorAgentNode)
        graph.add_node(ToolNode)

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.build().compile(checkpointer=checkpointer)
