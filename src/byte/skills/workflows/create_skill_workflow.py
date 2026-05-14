from byte.files.tools.add_files_tool import AddFilesTool
from byte.files.tools.list_files_tool import ListFilesTool
from byte.git.tools.git_grep_tool import GitGrepTool
from byte.node.nodes import ToolNode
from byte.orchestration import GraphBuilder
from byte.plan import CompletePlanStepTool, CreatePlanTool, PlanStep
from byte.skills import SkillCreatorAgentNode
from byte.skills.tools.create_skill_tool import CreateSkillTool
from byte.system.tools.user_confirm_tool import UserConfirmTool
from byte.system.tools.user_input_text_tool import UserInputTextTool
from byte.system.tools.user_select_tool import UserSelectTool
from byte.workflow import BaseWorkflow


class CreateSkillWorkflow(BaseWorkflow):
    """ """

    def get_plan(self):
        return [
            PlanStep(
                id="1",
                order=1,
                content="Capture intent — understand what the skill should do, when it triggers, and what the expected output looks like.",
                note=[
                    f"When possible use the `{CreatePlanTool.name}` tool in parallel with the `{CompletePlanStepTool.name}` tool",
                    f"Use `{UserInputTextTool.name}`, `{UserSelectTool.name}`, or `{UserConfirmTool.name}` to gather information from the user",
                    f"Use `{ListFilesTool.name}`, `{AddFilesTool.name}`, or `{GitGrepTool.name}` to gather additional context if needed",
                ],
                agent=SkillCreatorAgentNode,
                tools=[
                    CreatePlanTool,
                    UserInputTextTool,
                    UserSelectTool,
                    UserConfirmTool,
                    ListFilesTool,
                    AddFilesTool,
                    GitGrepTool,
                ],
            ),
            PlanStep(
                id="2",
                order=2,
                content="Create the skill — use available tools to create the skill with a clear name, description, and instructions.",
                agent=SkillCreatorAgentNode,
                tools=[
                    CreateSkillTool,
                ],
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
