from typing import Literal

from langgraph.graph.state import RunnableConfig
from langgraph.types import Command

from byte.development import RecordResponseService
from byte.node import (
    BaseAgentNode,
)
from byte.orchestration import BaseState, Leaves, PhaseUtils


class HarnessAgentNode(BaseAgentNode):
    llm_tier: str = "reasoning"

    def get_user_template(self):
        return [
            Leaves.ConversationHistory(),
            Leaves.UserRequest(),
        ]

    def get_system_template(self):
        return [
            Leaves.Preamble(
                role="Act as a harness selector. Your responsibility is to identify and load the relevant skills, files to edit, and reference files based on the user's task and the current workflow."
            ),
            Leaves.SkillsAvailable(),
            Leaves.CommunicationStyle(),
            Leaves.WorkflowConstraints(
                [
                    "Analyze the user's task and the available tools to determine what skills, editable files, and reference files are needed",
                    "Pass only the parameters required by the tools provided in the current phase",
                    "DO NOT answer the user's question or perform the task itself",
                    "DO NOT produce code, explanations, or plans",
                ]
            ),
            Leaves.OperatingPrinciples(),
        ]

    def get_context_template(self):
        return [
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
                prompt[-1].content[0]["text"] += (  # ty:ignore[invalid-argument-type]
                    " > ERROR: The workflow has incomplete phases, you MUST use the provided tools to complete the workflow."
                )
