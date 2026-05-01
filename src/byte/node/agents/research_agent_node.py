from typing import Literal, Type

from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.state import RunnableConfig
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
from byte.orchestration import BaseState
from byte.support import Section, SectionType, Str
from byte.support.utils import extract_content_from_message
from byte.web import SearchWebTool

user_template = [
    "{modified_messages}",
    "{user_request}",
    "",
    Section.start(SectionType.OPERATING_CONSTRAINTS),
    "- Always use best practices when researching and answering",
    "- Respect and use existing conventions, libraries, and patterns already present in the codebase",
    "- If the request is ambiguous, ask clarifying questions before proceeding",
    "- Keep responses focused — do not go beyond the scope of what was asked",
    "- Never use XML-style tags in your responses (e.g., <file>, <search>, <replace>). These are for internal parsing only.",
    "- Do not provide full code implementations unless explicitly requested. Describe findings and changes needed first.",
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


system_template = [
    "{preamble}",
    Section.start(SectionType.ROLE),
    "Act as an expert software developer and researcher. Your goal is to deeply investigate the codebase, gather relevant context using available tools, and deliver accurate, well-supported answers.",
    Section.end(),
    "{available_skills}",
]


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "{system_message}"),
        ("user", "{user_message}"),
        ("placeholder", "{scratch_messages}"),
        ("user", "{context_message}"),
    ]
)


class ResearchAgentNode(BaseAgentNode):
    def boot(
        self,
        goto: Type[BaseNode] = EndNode,
        **kwargs,
    ):
        self.goto = Str.class_to_snake_case(goto)

    @property
    def message_type(self) -> Type[BaseAIMessage]:
        return ByteAIMessage.AskAgentMessage

    def get_model(self) -> tuple[ModelSchema, dict]:
        llm_service = self.app.make(LLMService)
        return llm_service.get_model(self.name)

    def get_prompt(self):
        return prompt

    def get_user_template(self):
        return user_template

    def get_system_template(self):
        return system_template

    def get_tools(self, state: BaseState):
        from byte.lsp import FindReferencesTool, GetDefinitionTool, GetHoverInfoTool

        base_tools = [
            GitGrepTool,
            ListFilesTool,
            ReadFilesTool,
            SearchWebTool,
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
        return self.route_to(self.goto, {"scratch_messages": ByteAIMessage.AskAgentMessage(content=msg)})
