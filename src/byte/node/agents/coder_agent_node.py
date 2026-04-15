from typing import Literal, Type

from langchain.messages import AIMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.development import RecordResponseService
from byte.files import edit_file
from byte.llm import LLMService
from byte.node import (
    BaseAgentNode,
    BaseNode,
)
from byte.node.nodes import EndNode
from byte.orchestration import AssistantContextSchema, BaseState, preamble
from byte.support import Boundary, BoundaryType, Str
from byte.support.utils import extract_content_from_message, list_to_multiline_text
from byte.tui import Messages

coder_user_template = [
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
    "- If the request is ambiguous, ask clarifying questions before proceeding",
    "- Keep changes simple don't build more then what is asked for",
    Boundary.close(BoundaryType.OPERATING_CONSTRAINTS),
    # "{available_conventions}",
    # "{project_hierarchy}",
    "{project_information_and_context}",
    "{file_context}",
    "{operating_principles}",
]

coder_prompt = ChatPromptTemplate.from_messages(
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
        # ("placeholder", "{examples}"),
        ("user", "{assembled_user_message}"),
        ("placeholder", "{scratch_messages}"),
        ("placeholder", "{errors}"),
    ]
)


class CoderAgentNode(BaseAgentNode):
    def boot(
        self,
        goto: Type[BaseNode] = EndNode,
        **kwargs,
    ):
        """
        Initialize the CoderAgentNode with a target node to route to after execution.

        Args:
            goto: The target node class to route to after the agent completes. Defaults to EndNode.
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        self.goto = Str.class_to_snake_case(goto)

    def get_model(self) -> BaseChatModel:
        llm_service = self.app.make(LLMService)
        return llm_service.get_weak_model()

    def get_prompt(self):
        return coder_prompt

    def get_user_template(self):
        return coder_user_template

    def get_tools(self):
        return [edit_file]

    async def __call__(
        self,
        state: BaseState,
        *,
        runtime: Runtime[AssistantContextSchema],
        config: RunnableConfig,
    ) -> Command[Literal["routing_node"]]:

        agent_state, config = await self.generate_agent_state(state, config, runtime.context)
        runnable = self.create_runnable()
        record_response_service = self.app.make(RecordResponseService)

        await self.emit_tui(Messages.LoadingIndicatorShow())
        await self.emit_tui(Messages.AddHeading("Coder Agent", "text-primary"))
        await self.emit_tui(Messages.ResponseStarted())

        result = await runnable.ainvoke(agent_state, config=config)
        await record_response_service.record_response(agent_state, runnable, "coder_agent", config)

        await self.emit_tui(Messages.ResponseComplete())
        await self.emit_tui(Messages.LoadingIndicatorHide())

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
