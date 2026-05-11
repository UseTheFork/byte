from typing import Literal, Type

from langgraph.graph.state import RunnableConfig
from langgraph.types import Command

from byte.development import RecordResponseService
from byte.llm import LLMService, ModelSchema
from byte.node import (
    BaseAgentNode,
    BaseNode,
)
from byte.node.nodes import EndNode
from byte.orchestration import AIMessage, BaseState, Leaves
from byte.support import Section, SectionType, Str
from byte.support.utils import extract_content_from_message


class ConstitutionAgentNode(BaseAgentNode):
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

    def get_model(self) -> tuple[ModelSchema, dict]:
        llm_service = self.app.make(LLMService)
        return llm_service.get_model(self.name)

    def get_user_template(self):
        return [
            Leaves.UserRequest(),
        ]

    def get_system_template(self):
        return [
            Leaves.Preamble(
                role=f"You are updating the project constitution at {Section.ref(SectionType.CONSTITUTION)}. Your job is to (a) collect/derive concrete values, (b) fill the template precisely, and (c) propagate any amendments across dependent artifacts."
            ),
            Leaves.OperatingPrinciples(),
        ]

    def get_context_template(self):
        return [
            Leaves.Constitution(),
            Leaves.ToolsLoaded(),
            Leaves.ReferenceMaterials(),
            Leaves.ProjectEnvironment(),
            Leaves.FileContext(),
            Leaves.PlanPending(),
            Leaves.Epilogue(),
        ]

    async def __call__(
        self,
        state: BaseState,
        *,
        config: RunnableConfig,
    ) -> Command[Literal["routing_node"]]:

        runnable = self.create_runnable(state)

        agent_state, config = await self.generate_agent_state(state, config)
        record_response_service = self.app.make(RecordResponseService)

        self.app.dispatch_task(
            record_response_service.record_response(agent_state, runnable, self.name, config),
        )
        result = await runnable.ainvoke(
            agent_state,
            config=config,
            cache_control={"type": "ephemeral"},
        )

        route_tool_call = self.route_tool_calls(result)
        if route_tool_call is not None:
            return route_tool_call

        msg = extract_content_from_message(result)
        return self.route_to(self.goto, {"scratch_messages": AIMessage(content=msg, agent_name=self.name)})
