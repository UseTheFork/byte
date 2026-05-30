from typing import Literal

from langgraph.graph.state import RunnableConfig
from langgraph.types import Command

from byte.node import (
    BaseAgentNode,
)
from byte.orchestration import BaseState, Leaves, PhaseUtils


class SpecCreatorAgentNode(BaseAgentNode):
    llm_tier: str = "standard"

    def get_user_template(self):
        return [
            Leaves.ReferenceMaterials(),
            Leaves.HarnessWorkspaceReferenceFiles(),
            Leaves.UserRequest(),
        ]

    def get_system_template(self):
        return [
            Leaves.Preamble(
                role="Act as an expert spec creator. Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste."
            ),
            Leaves.Constitution(),
            Leaves.OperatingPrinciples(),
            Leaves.CommunicationStyle(verbose=True),
            Leaves.WorkflowConstraints(
                [
                    "Understand what the user wants the spec to cover before writing anything",
                    "If the request is ambiguous, ask clarifying questions about intent, scope, and success criteria",
                    "Keep spec instructions clear, concise, and actionable",
                ]
            ),
        ]

    def get_context_template(self):
        return [
            Leaves.ReferenceMaterials(),
            Leaves.ProjectEnvironment(),
            Leaves.HarnessWorkspaceFiles(),
            Leaves.WorkflowPending(),
            Leaves.Epilogue(),
            Leaves.ToolsLoaded(),
        ]

    async def __call__(
        self,
        state: BaseState,
        *,
        config: RunnableConfig,
    ) -> Command[Literal["routing_node"]]:

        prompt_assembler = await self.generate_agent_state(state, config)
        runnable = self.create_runnable(prompt_assembler)
        prompt = await self.generate_prompt(prompt_assembler)

        while True:
            result = await runnable.ainvoke(
                prompt,
                config=config,
            )
            await self.finalize_response(result, prompt, config)

            route_tool_call = self.route_tool_calls(result)
            if route_tool_call is not None:
                return route_tool_call

            if not PhaseUtils.is_workflow_complete(prompt_assembler.get_state()):
                prompt[-1].content[0]["text"] += (  # ty:ignore[invalid-argument-type]
                    " > ERROR: The workflow has incomplete phases, you MUST use the provided tools to complete the workflow."
                )
