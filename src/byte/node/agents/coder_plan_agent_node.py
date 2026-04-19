from typing import Literal, Type

from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.development import RecordResponseService
from byte.llm import LLMService, ModelSchema
from byte.node import (
    BaseAgentNode,
    BaseNode,
)
from byte.node.agents import CoderAgentNode
from byte.orchestration import (
    AssistantContextSchema,
    BaseState,
    preamble,
)
from byte.support import Boundary, BoundaryType, Str
from byte.support.utils import extract_content_from_message, list_to_multiline_text
from byte.tui import Messages, Status

coder_plan_user_template = [
    "{masked_messages}",
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
    "- Do NOT provide full code implementations - only describe what needs to change",
    "- May include pseudo code if helpful for clarity",
    "- Keep the plan concise and actionable",
    Boundary.close(BoundaryType.OPERATING_CONSTRAINTS),
    "",
    "{project_information_and_context}",
    "",
    "{file_context_with_line_numbers}",
    "",
    Boundary.open(BoundaryType.TASK),
    "Your task is to create a clear, step-by-step plan for implementing the requested changes.",
    "The plan will be used by another agent to make the actual code changes.",
    "",
    Boundary.open(BoundaryType.RESPONSE_FORMAT),
    "Format your plan as follows:",
    "1. Start with a brief summary: 'To make this change we need to modify/create/delete [file(s)]:'",
    "2. Leave a blank line",
    "3. List each step numerically with clear, actionable descriptions",
    "4. Do NOT include actual code unless it's brief pseudo code for clarity",
    "",
    Boundary.open(BoundaryType.EXAMPLE),
    "Example 1:",
    "```",
    "To make this change we need to modify `mathweb/flask/app.py` to:",
    "",
    "1. Import the math package.",
    "2. Remove the existing factorial() function.",
    "3. Update get_factorial() to call math.factorial instead.",
    "```",
    Boundary.close(BoundaryType.EXAMPLE),
    Boundary.open(BoundaryType.EXAMPLE),
    "Example 2:",
    "```",
    "To make this change we need to modify `main.py` and create a new file `hello.py`:",
    "",
    "1. Create a new hello.py file with a hello() function that prints a greeting.",
    "2. In main.py, remove the hello() function definition.",
    "3. In main.py, add an import statement for hello from hello.py.",
    "4. Update the main() function to call the imported hello().",
    "```",
    Boundary.close(BoundaryType.EXAMPLE),
    Boundary.open(BoundaryType.EXAMPLE),
    "Example 3:",
    "```",
    "To make this change we need to modify `services/auth.py` and `models/user.py`:",
    "",
    "1. In models/user.py, add a new field 'last_login' to the User class.",
    "2. In services/auth.py, import the datetime module.",
    "3. In the authenticate() method, update the user's last_login timestamp after successful authentication.",
    "```",
    Boundary.close(BoundaryType.EXAMPLE),
    Boundary.close(BoundaryType.RESPONSE_FORMAT),
    Boundary.close(BoundaryType.TASK),
    "{operating_principles}",
]

coder_plan_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            list_to_multiline_text(
                [
                    Boundary.open(BoundaryType.ROLE),
                    preamble(),
                    "Act as an expert software architect and planner.",
                    "Your role is to analyze requests and create clear, actionable implementation plans.",
                    "You do NOT implement code - you plan the changes that another agent will execute.",
                    Boundary.close(BoundaryType.ROLE),
                ]
            ),
        ),
        ("user", "{assembled_user_message}"),
        ("placeholder", "{scratch_messages}"),
    ]
)

coder_plan_enforcement = [
    "- NEVER use XML-style tags in your responses (e.g., <file>, <search>, <replace>). These are for internal parsing only.",
    "- DO NOT provide full code implementations unless explicitly requested. Describe the changes needed first.",
]


class CoderPlanAgentNode(BaseAgentNode):
    def boot(
        self,
        goto: Type[BaseNode] = CoderAgentNode,
        **kwargs,
    ):
        """ """

        self.goto = Str.class_to_snake_case(goto)

    def get_model(self) -> tuple[ModelSchema, dict]:
        llm_service = self.app.make(LLMService)
        return llm_service.get_model(self.name)

    def get_prompt(self):
        return coder_plan_prompt

    def get_user_template(self):
        return coder_plan_user_template

    def get_enforcement(self):
        return coder_plan_enforcement

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

        await self.emit_tui(Messages.AddHeading("Plan Agent", "text-primary"))
        await self.emit_tui(Messages.Response(status=Status.PENDING))

        result = await runnable.ainvoke(agent_state, config=config)
        await record_response_service.record_response(agent_state, runnable, "coder_plan_agent", config)

        await self.emit_tui(Messages.Response(status=Status.SUCCESS))

        if result.tool_calls and len(result.tool_calls) > 0:
            return self.route_to(
                "tool_node",
                {
                    "scratch_messages": [result],
                    "errors": None,
                },
            )

        # Replace the user request with the agent plan
        msg = extract_content_from_message(result)
        return self.route_to(self.goto, {"user_request": msg})
