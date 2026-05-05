from typing import Literal, Type

from langgraph.graph.state import RunnableConfig
from langgraph.types import Command

from byte.development import RecordResponseService
from byte.files import (
    DeleteFileTool,
    EditFileTool,
    ReplaceFileTool,
    WriteFileTool,
)
from byte.llm import LLMService, ModelSchema
from byte.memory import CompleteSimpleTurnTool
from byte.node import (
    BaseAgentNode,
    BaseNode,
)
from byte.node.nodes import EndNode
from byte.orchestration import AIMessage, BaseState, Leaves
from byte.support import Boundary, BoundaryType, Section, SectionType, Str
from byte.support.utils import extract_content_from_message

user_template = [
    Leaves.ConversationHistory(),
    Leaves.UserRequest(),
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
    "- PHASE 2: Use available tools to apply the changes.",
    "- PHASE 3: Provide a summary of what was changed.",
    "",
    "- For longer tasks, send brief progress updates (under 10 words) BUT IMMEDIATELY CONTINUE WORKING - progress updates are not stopping points",
    Section.sub_heading("Example Workflow", 2),
    "```",
    Boundary.open(BoundaryType.EXAMPLE),
    Boundary.open(BoundaryType.AGENT_MESSAGE),
    Section.sub_heading("Plan", 2),
    "To make this change we need to modify `main.py`:",
    "",
    "1. Remove the old function.",
    "2. Add a new helper function.",
    Boundary.close(BoundaryType.AGENT_MESSAGE),
    Boundary.open(BoundaryType.AGENT_MESSAGE),
    "Removing old function now.",
    Boundary.close(BoundaryType.AGENT_MESSAGE),
    Boundary.open(BoundaryType.TOOL_CALL),
    f"{EditFileTool.name}([removed for brevity])",
    Boundary.close(BoundaryType.TOOL_CALL),
    Boundary.open(BoundaryType.AGENT_MESSAGE),
    "Adding new helper function.",
    Boundary.close(BoundaryType.AGENT_MESSAGE),
    Boundary.open(BoundaryType.TOOL_CALL),
    f"{EditFileTool.name}([removed for brevity])",
    Boundary.close(BoundaryType.TOOL_CALL),
    Boundary.open(BoundaryType.AGENT_MESSAGE),
    f"All steps complete. Calling `{CompleteSimpleTurnTool.name}` to finalize.",
    Boundary.close(BoundaryType.AGENT_MESSAGE),
    Boundary.open(BoundaryType.TOOL_CALL),
    f'{CompleteSimpleTurnTool.name}(summary="Removed old function and added new helper function.")',
    Boundary.close(BoundaryType.TOOL_CALL),
    Boundary.close(BoundaryType.EXAMPLE),
    "```",
    "",
    Section.end(),
    "",
    Section.important(
        f"All tool operations are applied immediately and are reflected in the next user message containing {SectionType.PROJECT_FILES}."
    ),
]


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

    def get_model(self) -> tuple[ModelSchema, dict]:
        llm_service = self.app.make(LLMService)
        return llm_service.get_model(self.name)

    def get_user_template(self):
        return user_template

    def get_system_template(self):
        return [
            Leaves.Preamble(role="Act as an expert software developer."),
            Leaves.SkillsAvailable(),
            Leaves.OperatingPrinciples(),
        ]

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
        # Depending on the state we modify the returned tools.
        base_tools = []

        base_tools.extend(
            [
                EditFileTool,
                WriteFileTool,
                DeleteFileTool,
                ReplaceFileTool,
                CompleteSimpleTurnTool,
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
        return self.route_to(self.goto, {"scratch_messages": AIMessage(content=msg, agent_name=self.name)})
