from typing import Literal, Type

from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.development import RecordResponseService
from byte.files import delete_file, edit_file, replace_file, write_file
from byte.llm import LLMService, ModelSchema
from byte.node import (
    BaseAgentNode,
    BaseNode,
    ByteAIMessage,
)
from byte.node.messages import BaseAIMessage
from byte.node.nodes import EndNode
from byte.orchestration import AssistantContextSchema, BaseState, preamble
from byte.support import Boundary, BoundaryType, Str
from byte.support.utils import extract_content_from_message, list_to_multiline_text

coder_user_template = [
    "{modified_messages}",
    Boundary.open(BoundaryType.USER_INPUT),
    "```text",
    "{user_request}",
    "```",
    "",
    "You **MUST** consider the user input before proceeding (if not empty).",
    Boundary.close(BoundaryType.USER_INPUT),
    Boundary.open(BoundaryType.OPERATING_CONSTRAINTS),
    "- Analyze the user's request and the provided file context",
    "- If the request is ambiguous, ask clarifying questions",
    "- Identify which files need to be modified, created, or deleted",
    "- Break down the changes into clear, sequential steps",
    "- FIRST create a plan, THEN use available tools to implement the changes",
    "- Do NOT provide full code implementations unless required by tools",
    "- Keep the plan concise and actionable",
    Boundary.close(BoundaryType.OPERATING_CONSTRAINTS),
    "",
    "{project_information_and_context}",
    "",
    "",
    Boundary.open(BoundaryType.TASK),
    "Your task has THREE phases:",
    "",
    "PHASE 1: Create a clear, step-by-step plan for implementing the requested changes.",
    "PHASE 2: Use available tools to apply the changes.",
    f"Between each tool call you **MUST** reference the user message containing `{Boundary.open(BoundaryType.PROJECT_STATE)}` — this is always updated to reflect the current state of the project. Use it to continue executing your step-by-step plan from Phase 1.",
    "PHASE 3: Provide a summary of what was changed.",
    "",
    Boundary.open(BoundaryType.RESPONSE_FORMAT),
    "Format your response as follows:",
    "",
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
    "",
    Boundary.open(BoundaryType.EXAMPLE),
    "Example:",
    "```",
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
    "```",
    Boundary.close(BoundaryType.EXAMPLE),
    Boundary.close(BoundaryType.RESPONSE_FORMAT),
    Boundary.close(BoundaryType.TASK),
    "{operating_principles}",
    "",
    Boundary.critical(
        f"All tool operations are applied immediately and are reflected in the `{Boundary.open(BoundaryType.PROJECT_STATE)}`."
    ),
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
        ("user", "{assembled_user_message}"),
        ("placeholder", "{scratch_messages}"),
        ("placeholder", "{refreshed_context}"),
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
        return [edit_file, write_file, delete_file, replace_file]

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

        # Extract the last CoderPlanAgentMessage from scratch_messages
        last_coder_plan_message = None
        for msg in reversed(state.get("scratch_messages", [])):
            if isinstance(msg, ByteAIMessage.CoderPlanAgentMessage):
                last_coder_plan_message = msg
                break

        agent_state["coder_plan_agent_request"] = last_coder_plan_message.content if last_coder_plan_message else ""

        result = await runnable.ainvoke(agent_state, config=config)
        self.app.dispatch_task(
            record_response_service.record_response(agent_state, runnable, self.name, config),
        )

        route_tool_call = self.route_tool_calls(result)
        if route_tool_call is not None:
            return route_tool_call

        msg = extract_content_from_message(result)
        return self.route_to(self.goto, {"scratch_messages": ByteAIMessage.CoderAgentMessage(content=msg)})
