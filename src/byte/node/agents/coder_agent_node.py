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
from byte.memory import CompleteStepTool, CompleteTurnTool, CreatePlanTool
from byte.node import (
    BaseAgentNode,
    BaseNode,
    ByteAIMessage,
)
from byte.node.messages import BaseAIMessage
from byte.node.nodes import EndNode
from byte.orchestration import AssistantContextSchema, BaseState, preamble
from byte.skills.tools.load_skill_tool import LoadSkillTool
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
    Section.start(SectionType.COMMUNICATION_STYLE),
    "- ALWAYS think and respond in the same spoken language the prompt was written in.",
    "- Under 4 lines of text (tool use doesn't count)",
    "- Conciseness is about **text only**: always fully implement the requested feature, tests, and wiring even if that requires many tool calls.",
    """- No preamble ("Here's...", "I'll...")""",
    """- No postamble ("Let me know...", "Hope this helps...")""",
    "- No emojis ever",
    "- No explanations unless user asks",
    "- Never send acknowledgement-only responses; after receiving new context or instructions, immediately continue the task or state the concrete next action you will take.",
    "- Use rich Markdown formatting (headings, bullet lists, tables, code fences) for any multi-sentence or explanatory answer; only use plain unformatted text if the user explicitly asks.",
    Section.end(),
    Section.start(SectionType.WORKFLOW),
    "For every task, follow this sequence internally (don't narrate it):",
    "",
    "- PHASE 1: Create a clear, step-by-step plan for implementing the requested changes.",
    f"    You MUST use the `{CreatePlanTool.name}` tool for this.",
    "- PHASE 2: Use available tools to apply the changes.",
    f"    Once you complete a step use the `{CompleteStepTool.name}` tool to mark it complete.",
    "- PHASE 3: Provide a summary of what was changed.",
    "",
    "- For longer tasks, send brief progress updates (under 10 words) BUT IMMEDIATELY CONTINUE WORKING - progress updates are not stopping points",
    Section.sub_heading("Example Workflow", 2),
    "```",
    Boundary.open(BoundaryType.EXAMPLE),
    Boundary.open(BoundaryType.AGENT_MESSAGE),
    "Creating plan for the requested changes.",
    Boundary.close(BoundaryType.AGENT_MESSAGE),
    Boundary.open(BoundaryType.TOOL_CALL),
    f'{CreatePlanTool.name}(steps=[{{"order": 1, "content": "Remove the old function."}}, {{"order": 2, "content": "Add a new helper function."}}])',
    Boundary.close(BoundaryType.TOOL_CALL),
    Boundary.open(BoundaryType.AGENT_MESSAGE),
    "Removing old function now.",
    Boundary.close(BoundaryType.AGENT_MESSAGE),
    Boundary.open(BoundaryType.TOOL_CALL),
    f"{EditFileTool.name}([removed for brevity])",
    Boundary.close(BoundaryType.TOOL_CALL),
    Boundary.open(BoundaryType.TOOL_CALL),
    f'{CompleteStepTool.name}(step_id="1")',
    Boundary.close(BoundaryType.TOOL_CALL),
    Boundary.open(BoundaryType.AGENT_MESSAGE),
    "Adding new helper function.",
    Boundary.close(BoundaryType.AGENT_MESSAGE),
    Boundary.open(BoundaryType.TOOL_CALL),
    f"{EditFileTool.name}([removed for brevity])",
    Boundary.close(BoundaryType.TOOL_CALL),
    Boundary.open(BoundaryType.TOOL_CALL),
    f'{CompleteStepTool.name}(step_id="2")',
    Boundary.close(BoundaryType.TOOL_CALL),
    Boundary.open(BoundaryType.AGENT_MESSAGE),
    f"All steps complete. Calling `{CompleteTurnTool.name}` to finalize.",
    Boundary.close(BoundaryType.AGENT_MESSAGE),
    Boundary.open(BoundaryType.TOOL_CALL),
    f'{CompleteTurnTool.name}(summary="Removed old function and added new helper function.", key_points=[])',
    Boundary.close(BoundaryType.TOOL_CALL),
    Boundary.close(BoundaryType.EXAMPLE),
    "```",
    "",
    Section.end(),
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
            CreatePlanTool,
            CompleteStepTool,
            CompleteTurnTool,
            EditFileTool,
            WriteFileTool,
            DeleteFileTool,
            ReplaceFileTool,
            LoadSkillTool,
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
