from typing import Literal, Type

from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.development import RecordResponseService
from byte.files import ListFilesTool, ReadFilesTool
from byte.git import GitGrepTool
from byte.llm import LLMService, ModelSchema
from byte.node import (
    BaseAgentNode,
    BaseNode,
    ByteAIMessage,
)
from byte.node.messages import BaseAIMessage
from byte.node.nodes import EndNode
from byte.orchestration import (
    AssistantContextSchema,
    BaseState,
    preamble,
)
from byte.support import Section, SectionType, Str
from byte.support.utils import extract_content_from_message, list_to_multiline_text
from byte.system import UserSelectTool
from byte.web import SearchWebTool

ask_user_template = [
    "{modified_messages}",
    "{user_request}",
    "",
    Section.start(SectionType.OPERATING_CONSTRAINTS),
    "- Always use best practices when coding",
    "- Respect and use existing conventions, libraries, etc that are already present in the code base",
    "- Take requests for changes to the supplied code",
    "- If the request is ambiguous, ask questions",
    "- Keep changes simple don't build more then what is asked for",
    "- Never use XML-style tags in your responses (e.g., <file>, <search>, <replace>). These are for internal parsing only.",
    "- Do not provide full code implementations unless explicitly requested. Describe the changes needed first.",
    Section.end(),
    "",
    Section.start(SectionType.RESPONSE_FORMAT),
    "- Use clear, concise explanations",
    "- Format code with proper syntax highlighting",
    "- Provide context for suggested changes",
    "- Focus on actionable findings, not exhaustive documentation",
    Section.end(),
    "",
    "{operating_principles}",
]

ask_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            list_to_multiline_text(
                [
                    preamble(),
                    Section.start(SectionType.ROLE),
                    "Act as an expert software developer.",
                    Section.end(),
                ]
            ),
        ),
        ("user", "{assembled_user_message}"),
        ("placeholder", "{scratch_messages}"),
        ("placeholder", "{refreshed_context_state}"),
        ("placeholder", "{errors}"),
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

    @property
    def message_type(self) -> Type[BaseAIMessage]:
        return ByteAIMessage.AskAgentMessage

    def get_model(self) -> tuple[ModelSchema, dict]:
        llm_service = self.app.make(LLMService)
        return llm_service.get_model(self.name)

    def get_prompt(self):
        return ask_prompt

    def get_user_template(self):
        return ask_user_template

    def get_enforcement(self):
        return ask_enforcement

    def get_tools(self, state: BaseState):
        return [
            GitGrepTool,
            UserSelectTool,
            ListFilesTool,
            ReadFilesTool,
            SearchWebTool,
        ]

    async def __call__(
        self,
        state: BaseState,
        *,
        runtime: Runtime[AssistantContextSchema],
        config: RunnableConfig,
    ) -> Command[Literal["routing_node"]]:

        runnable = self.create_runnable(state)

        agent_state, config = await self.generate_agent_state(state, config)
        record_response_service = self.app.make(RecordResponseService)

        self.app.dispatch_task(
            record_response_service.record_response(agent_state, runnable, self.name, config),
        )
        result = await runnable.ainvoke(agent_state, config=config)

        route_tool_call = self.route_tool_calls(result)
        if route_tool_call is not None:
            return route_tool_call

        msg = extract_content_from_message(result)
        return self.route_to(self.goto, {"scratch_messages": ByteAIMessage.AskAgentMessage(content=msg)})
