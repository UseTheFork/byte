from typing import Literal, Type

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.development import RecordResponseService
from byte.git import git_grep
from byte.llm import LLMService, ModelSchema
from byte.node import (
    BaseAgentNode,
    BaseNode,
)
from byte.node.nodes import EndNode
from byte.orchestration import (
    AssistantContextSchema,
    BaseState,
    preamble,
)
from byte.support import Boundary, BoundaryType, Str
from byte.support.utils import extract_content_from_message, list_to_multiline_text
from byte.tui import Messages, Status

ask_user_template = [
    "{masked_messages}",
    Boundary.open(BoundaryType.USER_INPUT),
    "```text",
    "{user_request}",
    "```",
    "",
    "You **MUST** consider the user input before proceeding (if not empty).",
    Boundary.close(BoundaryType.USER_INPUT),
    Boundary.open(BoundaryType.OPERATING_CONSTRAINTS),
    "- Always use best practices when coding",
    "- Respect and use existing conventions, libraries, etc that are already present in the code base",
    "- Take requests for changes to the supplied code",
    "- If the request is ambiguous, ask questions",
    "- Keep changes simple don't build more then what is asked for",
    "- Never use XML-style tags in your responses (e.g., <file>, <search>, <replace>). These are for internal parsing only.",
    "- Do not provide full code implementations unless explicitly requested. Describe the changes needed first.",
    Boundary.close(BoundaryType.OPERATING_CONSTRAINTS),
    "",
    Boundary.open(BoundaryType.RESPONSE_FORMAT),
    "- Use clear, concise explanations",
    "- Format code with proper syntax highlighting",
    "- Provide context for suggested changes",
    "- Focus on actionable findings, not exhaustive documentation",
    Boundary.close(BoundaryType.RESPONSE_FORMAT),
    "{available_conventions}",
    "{project_hierarchy}",
    "{project_information_and_context}",
    "{file_context}",
    "{operating_principles}",
]

ask_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            list_to_multiline_text(
                [
                    Boundary.open(BoundaryType.ROLE),
                    preamble(),
                    "Act as an expert software developer.",
                    Boundary.close(BoundaryType.ROLE),
                ]
            ),
        ),
        ("user", "{assembled_user_message}"),
        ("placeholder", "{scratch_messages}"),
    ]
)

ask_enforcement = [
    "- NEVER use XML-style tags in your responses (e.g., <file>, <search>, <replace>). These are for internal parsing only.",
    "- DO NOT provide full code implementations unless explicitly requested. Describe the changes needed first.",
]


class AskAgentNode(BaseAgentNode):
    def boot(
        self,
        goto: Type[BaseNode] = EndNode,
        **kwargs,
    ):
        """Initialize the validation node with constraints and routing configuration.

        Args:
                goto: Next node to route to after successful validation (default: "end_node")
                max_lines: Maximum number of non-blank lines allowed in response content (optional)

        Usage: `await node.boot(goto="end_node", max_lines=100)`
        """

        self.goto = Str.class_to_snake_case(goto)

    def get_model(self) -> tuple[ModelSchema, dict]:
        llm_service = self.app.make(LLMService)
        return llm_service.get_model("ask")

    def get_prompt(self):
        return ask_prompt

    def get_user_template(self):
        return ask_user_template

    def get_enforcement(self):
        return ask_enforcement

    def get_tools(self):
        return [git_grep]
        # return [load_convention, git_grep]

    async def __call__(
        self,
        state: BaseState,
        *,
        runtime: Runtime[AssistantContextSchema],
        config: RunnableConfig,
    ) -> Command[Literal["routing_node"]]:
        runnable = self.create_runnable()

        agent_state, config = await self.generate_agent_state(state, config)
        record_response_service = self.app.make(RecordResponseService)

        await self.emit_tui(Messages.AddHeading("Ask Agent", "text-primary"))
        await self.emit_tui(Messages.Response(status=Status.PENDING))

        result = await runnable.ainvoke(agent_state, config=config)
        await record_response_service.record_response(agent_state, runnable, "ask_agent", config)

        await self.emit_tui(Messages.Response(status=Status.SUCCESS))

        if result.tool_calls and len(result.tool_calls) > 0:
            return self.route_to(
                "tool_node",
                {
                    "scratch_messages": [result],
                    "errors": None,
                },
            )

        msg = extract_content_from_message(result)
        return self.route_to(self.goto, {"scratch_messages": AIMessage(msg)})
