from typing import Literal

from langchain.messages import HumanMessage
from langgraph.graph.state import RunnableConfig
from langgraph.types import Command

from byte.development import RecordResponseService
from byte.node import (
    BaseAgentNode,
)
from byte.orchestration import BaseState, Leaves, PhaseUtils
from byte.skills.tools.load_skill_tool import LoadSkillTool


class SkillSelectAgentNode(BaseAgentNode):
    llm_tier: str = "reasoning"

    def get_user_template(self):
        return [
            Leaves.ConversationHistory(),
            Leaves.UserRequest(),
        ]

    def get_system_template(self):
        return [
            Leaves.Preamble(
                role="Act as a skill selector. Your sole responsibility is to identify and load the relevant skills based on the user's task."
            ),
            Leaves.SkillsAvailable(),
            Leaves.CommunicationStyle(),
            Leaves.WorkflowConstraints(
                [
                    "  - Analyze the user's task and identify which available skills are relevant",
                    f"  - Use the `{LoadSkillTool.name}` to load each relevant skill — do not perform any other work",
                    "  - Do NOT answer the user's question or perform the task itself",
                    "  - Do NOT produce code, explanations, or plans",
                    "  - Load only skills that are directly applicable to the user's task",
                ]
            ),
            Leaves.OperatingPrinciples(),
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

    def get_tools(self, state: BaseState):
        return [
            LoadSkillTool,
        ]

    async def __call__(
        self,
        state: BaseState,
        *,
        config: RunnableConfig,
    ) -> Command[Literal["routing_node"]]:

        record_response_service = self.app.make(RecordResponseService)
        prompt_assembler = await self.generate_agent_state(state, config)
        runnable = self.create_runnable(prompt_assembler)
        prompt = await self.generate_prompt(prompt_assembler)

        while True:
            result = await runnable.ainvoke(
                prompt,
                config=config,
            )
            self.app.dispatch_task(
                record_response_service.record_response(prompt, config),
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
