from typing import Literal

from langgraph.graph.state import RunnableConfig
from langgraph.types import Command

from byte.node import (
    BaseAgentNode,
)
from byte.orchestration import BaseState, Leaves, PhaseModel, PhaseUtils
from byte.support import Section, SectionType


class ConstitutionAgentNode(BaseAgentNode):
    llm_tier: str = "reasoning"

    def get_user_template(self):
        return [
            Leaves.UserRequest(),
        ]

    def get_system_template(self):
        return [
            Leaves.Preamble(
                role=f"Act as a project governance architect. You are updating the project constitution at {Section.ref(SectionType.CONSTITUTION)}."
            ),
            Leaves.CommunicationStyle(
                verbose=True,
            ),
            Leaves.WorkflowConstraints(
                [
                    "Your job is to (a) collect/derive concrete values",
                    "(b) fill the template precisely",
                    "(c) propagate any amendments across dependent artifacts.",
                ]
            ),
            Leaves.OperatingPrinciples(),
        ]

    def get_context_template(self):
        return [
            Leaves.Constitution(),
            Leaves.ToolsLoaded(),
            Leaves.ProjectEnvironment(),
            Leaves.HarnessWorkspaceReferenceContext(),
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

        # TODO: we should make this a static method in PhaseUtils
        pending_phase = PhaseUtils.get_pending_phase(prompt_assembler.get_state())
        if pending_phase is not None and isinstance(pending_phase, PhaseModel):
            runnable = self.create_runnable(prompt_assembler, tool_choice=pending_phase.tool_choice)
        else:
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
                    " > **ERROR**: The workflow has incomplete phases, you MUST use the provided tools to complete the workflow."
                )
