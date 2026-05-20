from typing import Literal, Type

from langchain.messages import HumanMessage
from langgraph.graph.state import RunnableConfig
from langgraph.types import Command

from byte.development import RecordResponseService
from byte.llm import LLMService, ModelSchema
from byte.node import (
    BaseAgentNode,
    BaseNode,
)
from byte.node.nodes import EndNode
from byte.orchestration import BaseState, Leaves, PhaseUtils
from byte.support import Section, Str


class SpecCreatorAgentNode(BaseAgentNode):
    def boot(
        self,
        goto: Type[BaseNode] = EndNode,
        **kwargs,
    ):
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
                role="Act as an expert spec creator. Your job is to help users design and create specs by understanding their intent, asking the right questions, and producing clear, well-structured spec definitions."
            ),
            Leaves.OperatingPrinciples(),
            Leaves.CommunicationStyle(verbose=True),
            Leaves.WorkflowConstraints(
                [
                    "- Understand what the user wants the spec to cover before writing anything",
                    "- If the request is ambiguous, ask clarifying questions about intent, scope, and success criteria",
                    "- Keep spec instructions clear, concise, and actionable",
                ]
            ),
            Section.end(),
        ]

    def get_context_template(self):
        return [
            Leaves.SkillsLoaded(),
            Leaves.ToolsLoaded(),
            Leaves.ReferenceMaterials(),
            Leaves.ProjectEnvironment(),
            Leaves.FileContext(),
            Leaves.WorkflowPending(),
            Leaves.Epilogue(),
        ]

    async def __call__(
        self,
        state: BaseState,
        *,
        config: RunnableConfig,
    ) -> Command[Literal["routing_node"]]:

        prompt_assembler = await self.generate_agent_state(state, config)
        runnable = self.create_runnable(prompt_assembler)
        record_response_service = self.app.make(RecordResponseService)
        prompt = await self.generate_prompt(prompt_assembler)

        while True:
            result = await runnable.ainvoke(
                prompt,
                config=config,
            )
            self.app.dispatch_task(
                record_response_service.record_response(prompt, self.name, config),
            )

            route_tool_call = self.route_tool_calls(result)
            if route_tool_call is not None:
                return route_tool_call

            if not PhaseUtils.is_workflow_complete(prompt_assembler.get_state()):
                prompt = prompt.extend(  # ty:ignore[unresolved-attribute]
                    [
                        HumanMessage(
                            content=[
                                {
                                    "type": "text",
                                    "text": "The workflow has incomplete phases, use the provided tools to complete the workflow.",
                                },
                            ]
                        )
                    ]
                )
