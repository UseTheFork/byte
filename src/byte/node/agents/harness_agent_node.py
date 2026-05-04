from typing import Literal, Type

from langgraph.graph.state import RunnableConfig
from langgraph.types import Command

from byte.development import RecordResponseService
from byte.harness import BootstrapAgentTool
from byte.llm import LLMService, ModelSchema
from byte.memory import CompleteStepTool, CompleteTurnTool, CreatePlanTool
from byte.node import (
    BaseAgentNode,
    BaseNode,
    ByteAIMessage,
)
from byte.node.messages import BaseAIMessage
from byte.node.nodes import EndNode
from byte.orchestration import BaseState, Leaves
from byte.support import Section, SectionType, Str
from byte.support.utils import extract_content_from_message

system_template = [
    "{preamble}",
    Section.start(SectionType.ROLE),
    "Act as an expert software developer.",
    Section.end(),
    "{all_skills}",
    "{all_tools}",
]

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
    Section.end(),
    "{operating_principles}",
    "",
    Section.important(
        f"All tool operations are applied immediately and are reflected in the next user message containing {SectionType.PROJECT_FILES}."
    ),
]


class HarnessAgentNode(BaseAgentNode):
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

    @property
    def message_type(self) -> Type[BaseAIMessage]:
        return ByteAIMessage.CoderAgentMessage

    def get_model(self) -> tuple[ModelSchema, dict]:
        llm_service = self.app.make(LLMService)
        return llm_service.get_model(self.name)

    def get_user_template(self):
        return user_template

    def get_system_template(self):
        return system_template

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
                BootstrapAgentTool,
                CompleteStepTool,
                CompleteTurnTool,
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
        return self.route_to(self.goto, {"scratch_messages": ByteAIMessage.CoderAgentMessage(content=msg)})
