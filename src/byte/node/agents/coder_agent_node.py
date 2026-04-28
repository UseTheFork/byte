from typing import Literal, Type

from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.development import RecordResponseService
from byte.files import (
    DeleteFileTool,
    EditFileTool,
    ReplaceFileTool,
    WriteFileTool,
)
from byte.llm import LLMService, ModelSchema
from byte.node import (
    BaseAgentNode,
    BaseNode,
    ByteAIMessage,
)
from byte.node.messages import BaseAIMessage
from byte.node.nodes import EndNode
from byte.orchestration import AssistantContextSchema, BaseState, preamble
from byte.support import Boundary, BoundaryType, Section, SectionType, Str
from byte.support.utils import extract_content_from_message, list_to_multiline_text

coder_user_template = [
    "{modified_messages}",
    "{user_request}",
    "",
    Section.start(SectionType.OPERATING_CONSTRAINTS),
    "- Analyze the user's request and the provided file context",
    "- If the request is ambiguous, ask clarifying questions",
    "- Identify which files need to be modified, created, or deleted",
    "- Break down the changes into clear, sequential steps",
    "- FIRST create a plan, THEN use available tools to implement the changes",
    "- Do NOT provide full code implementations unless required by tools",
    "- Keep the plan concise and actionable",
    Section.end(),
    "",
    "{project_information_and_context}",
    "",
    "",
    Section.start(SectionType.TASK),
    "Your task has THREE phases:",
    "",
    "- PHASE 1: Create a clear, step-by-step plan for implementing the requested changes.",
    "- PHASE 2: Use available tools to apply the changes.",
    # f"Between each tool call you **MUST** reference the user message containing `{SectionType.PROJECT_STATE}` - this is always updated to reflect the current state of the project. Use it to continue executing your step-by-step plan.",
    "- PHASE 3: Provide a summary of what was changed.",
    Section.end(),
    "",
    Section.start(SectionType.RESPONSE_FORMAT),
    "Format your response as follows:",
    "",
    "```md",
    "## Plan",
    "1. Start with a brief summary: 'To make this change we need to modify/create/delete [file(s)]:'",
    "2. Leave a blank line",
    "3. List each step numerically with clear, actionable descriptions",
    "4. Do NOT include full code unless necessary (pseudo code allowed)",
    "",
    "## Implementation",
    "- Use the available tools to perform the changes",
    "",
    "## Summary",
    "**Summary** - SHORT, CONCISE bulleted list of what was changed",
    "```",
    Section.end(),
    "",
    Section.start(SectionType.EXAMPLES),
    "",
    "```",
    Boundary.open(BoundaryType.EXAMPLE),
    "## Plan",
    "To make this change we need to modify `main.py`:",
    "",
    "1. Remove the old function.",
    "2. Add a new helper function.",
    "",
    "## Implementation",
    "[tool usage here]",
    "",
    "## Summary",
    "- Removed old function",
    "- Added helper function",
    Boundary.close(BoundaryType.EXAMPLE),
    "```",
    "",
    Section.end(),
    "",
    "{operating_principles}",
    "",
    Section.important(
        f"All tool operations are applied immediately and are reflected in the next user message containing {SectionType.PROJECT_STATE} #id-dhd88-asx-4857."
    ),
]

coder_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            list_to_multiline_text(
                [
                    preamble(),
                    "",
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

    @property
    def message_type(self) -> Type[BaseAIMessage]:
        return ByteAIMessage.CoderAgentMessage

    def get_model(self) -> tuple[ModelSchema, dict]:
        llm_service = self.app.make(LLMService)
        return llm_service.get_model(self.name)

    def get_prompt(self):
        return coder_prompt

    def get_user_template(self):
        return coder_user_template

    def get_tools(self):
        return [
            EditFileTool,
            WriteFileTool,
            DeleteFileTool,
            ReplaceFileTool,
        ]

    async def __call__(
        self,
        state: BaseState,
        *,
        runtime: Runtime[AssistantContextSchema],
        config: RunnableConfig,
    ) -> Command[Literal["routing_node"]]:

        agent_state, config = await self.generate_agent_state(state, config)
        runnable = self.create_runnable()
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
