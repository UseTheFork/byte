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
from byte.memory import CompleteStepTool, CompleteTurnTool, CreatePlanTool
from byte.node import (
    BaseAgentNode,
    BaseNode,
)
from byte.node.nodes import EndNode
from byte.orchestration import BaseState
from byte.orchestration.messages import AIMessage
from byte.skills.tools.load_skill_tool import LoadSkillTool
from byte.support import Boundary, BoundaryType, Section, SectionType, State, Str
from byte.support.utils import extract_content_from_message

user_template = [
    "{modified_messages}",
    "{user_request}",
    "",
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
        f"All tool operations are applied immediately and are reflected in the next user message containing {SectionType.PROJECT_FILES}."
    ),
]


system_template = [
    "{preamble}",
    Section.start(SectionType.ROLE),
    "Act as an expert software developer.",
    Section.end(),
    "{available_skills}",
]


class ExecutorAgentNode(BaseAgentNode):
    def boot(
        self,
        goto: Type[BaseNode] = EndNode,
        **kwargs,
    ):
        """
        Initialize the HarnessAgentNode with a target node to route to after execution.

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
        return system_template

    def get_tools(self, state: BaseState):
        # Depending on the state we modify the returned tools.
        base_tools = []

        if not State.has_plan(state):
            base_tools.append(CreatePlanTool)
        else:
            base_tools.extend(
                [
                    CompleteStepTool,
                    CompleteTurnTool,
                    EditFileTool,
                    WriteFileTool,
                    DeleteFileTool,
                    ReplaceFileTool,
                    LoadSkillTool,
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
        runnable = self.create_runnable(state, "any")
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
