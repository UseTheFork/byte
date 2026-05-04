from typing import Literal, Type

from langgraph.graph.state import RunnableConfig
from langgraph.types import Command

from byte.development import RecordResponseService
from byte.files.tools.add_files_tool import AddFilesTool
from byte.files.tools.list_files_tool import ListFilesTool
from byte.git.tools.git_grep_tool import GitGrepTool
from byte.llm import LLMService, ModelSchema
from byte.lsp import FindReferencesTool, GetDefinitionTool, GetHoverInfoTool
from byte.node import (
    BaseAgentNode,
    BaseNode,
    ByteAIMessage,
)
from byte.node.messages import BaseAIMessage
from byte.node.nodes import EndNode
from byte.orchestration import BaseState, Leaves
from byte.skills.tools.create_skill_tool import CreateSkillTool
from byte.support import Boundary, BoundaryType, Section, SectionType, Str
from byte.support.utils import extract_content_from_message
from byte.system.tools.user_confirm_tool import UserConfirmTool
from byte.system.tools.user_input_text_tool import UserInputTextTool
from byte.system.tools.user_select_tool import UserSelectTool

user_template = [
    Leaves.ConversationHistory(),
    Leaves.UserRequest(),
    Section.start(SectionType.OPERATING_CONSTRAINTS),
    "- Understand what the user wants the skill to do before writing anything",
    "- If the request is ambiguous, ask clarifying questions about intent, expected output, and when the skill should trigger",
    "- Capture the skill's name, description, and instructions before creating it",
    "- FIRST gather the necessary information, THEN use available tools to create the skill",
    "- Keep skill instructions clear, concise, and actionable",
    Section.end(),
    Section.start(SectionType.TASK),
    "Your task is to help the user create a new skill. Follow these phases:",
    "",
    "- PHASE 1: Capture Intent — Understand what the skill should do, when it should trigger, and what the expected output looks like.",
    "- PHASE 2: Interview — Ask about edge cases, input/output formats, and any dependencies. Come prepared with context.",
    f"    - Use the `{UserInputTextTool.name}`, `{UserSelectTool.name}` or the `{UserConfirmTool.name}` tools to do this.",
    "- PHASE 3: Create the Skill — Use the available tools to create the skill with a clear name, description, and instructions.",
    Section.end(),
    Section.start(SectionType.RESPONSE_FORMAT),
    "Structure your responses as follows:",
    "",
    "```md",
    "## Understanding",
    "Summarise what the skill will do and when it should trigger.",
    "",
    "## Clarifying Questions (if needed)",
    "List any questions before proceeding.",
    "",
    "## Skill Details",
    "- **Name**: skill-name",
    "- **Description**: When to trigger and what it does.",
    "- **Instructions**: Step-by-step instructions the skill will follow.",
    "",
    "## Summary",
    "**Summary** - SHORT, CONCISE bulleted list of what was created",
    "```",
    Section.end(),
    Section.start(SectionType.EXAMPLES),
    "```",
    Boundary.open(BoundaryType.EXAMPLE),
    "## Understanding",
    "This skill will format raw CSV data into a structured markdown table whenever the user shares tabular data and asks for a clean output.",
    "",
    "## Skill Details",
    "- **Name**: csv-to-markdown",
    "- **Description**: Converts raw CSV data into a formatted markdown table. Use this skill whenever the user shares CSV data or asks for a table.",
    "- **Instructions**: Read the CSV input, parse headers and rows, and output a properly formatted markdown table.",
    "",
    "## Summary",
    "- Created `csv-to-markdown` skill",
    "- Skill triggers when the user shares CSV data or requests a table",
    Boundary.close(BoundaryType.EXAMPLE),
    "```",
    "",
    Section.end(),
]

system_template = [
    Leaves.Preamble(
        role="Act as an expert skill creator. Your job is to help users design and create skills by understanding their intent, asking the right questions, and producing clear, well-structured skill definitions."
    ),
    Leaves.SkillsAvailable(),
    Leaves.OperatingPrinciples(),
]


class SkillCreatorAgentNode(BaseAgentNode):
    def boot(
        self,
        goto: Type[BaseNode] = EndNode,
        **kwargs,
    ):
        self.goto = Str.class_to_snake_case(goto)

    @property
    def message_type(self) -> Type[BaseAIMessage]:
        return ByteAIMessage.CoderAgentMessage

    def get_model(self) -> tuple[ModelSchema, dict]:
        llm_service = self.app.make(LLMService)
        return llm_service.get_model(self.name)

    def get_user_template(self):
        return user_template

    def get_system_template(self):
        return system_template

    def get_context_template(self):
        return [
            Leaves.SkillsLoaded(),
            Leaves.ToolsLoaded(),
            Leaves.ReferenceMaterials(),
            Leaves.ProjectEnvironment(),
            Leaves.FileContext(),
            Leaves.Epilogue(),
        ]

    def get_tools(self, state: BaseState):

        base_tools = [
            CreateSkillTool,
            GitGrepTool,
            UserSelectTool,
            UserInputTextTool,
            UserConfirmTool,
            ListFilesTool,
            AddFilesTool,
        ]

        config = self.app["config"]
        if config.lsp.enable:
            base_tools.extend(
                [
                    FindReferencesTool,
                    GetDefinitionTool,
                    GetHoverInfoTool,
                ]
            )

        return base_tools

    async def __call__(
        self,
        state: BaseState,
        *,
        config: RunnableConfig,
    ) -> Command[Literal["routing_node"]]:

        agent_state, config = await self.generate_agent_state(state, config)
        runnable = self.create_runnable(state)
        record_response_service = self.app.make(RecordResponseService)

        result = await runnable.ainvoke(agent_state, config=config)
        self.app.dispatch_task(
            record_response_service.record_response(agent_state, runnable, self.name, config),
        )

        route_tool_call = self.route_tool_calls(result)
        if route_tool_call is not None:
            return route_tool_call

        msg = extract_content_from_message(result)
        return self.route_to(self.goto, {"scratch_messages": ByteAIMessage.CoderAgentMessage(content=msg)})
