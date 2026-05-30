from typing import Literal

from langgraph.graph.state import RunnableConfig
from langgraph.types import Command

from byte.node import (
    BaseAgentNode,
)
from byte.orchestration import BaseState, Leaves, PhaseModel, PhaseUtils
from byte.support import Section, SectionType


class CoderAgentNode(BaseAgentNode):
    llm_tier: str = "coding"

    def get_user_template(self):
        return [
            Leaves.ReferenceMaterials(),
            Leaves.HarnessWorkspaceReferenceFiles(),
            Leaves.HarnessInstruction(),
            Section.important(
                f"All tool operations are applied immediately and are reflected in the next user message containing {Section.ref(SectionType.PROJECT_FILES)}."
            ),
        ]

    def get_system_template(self):
        return [
            Leaves.Preamble(role="Act as an expert software developer."),
            Leaves.Constitution(),
            Leaves.CommunicationStyle(
                rich_markdown=False,
                extra_styles=[
                    "Conciseness is about **text only**: always fully implement the requested feature, tests, and wiring even if that requires many tool calls.",
                    "No explanations unless user asks",
                    "Never send acknowledgement-only responses; after receiving new context or instructions, immediately continue the task or state the concrete next action you will take.",
                ],
            ),
            Leaves.WorkflowConstraints(
                [
                    "Analyze the user's request and the provided file context",
                    "If the request is ambiguous, ask clarifying questions",
                    "Identify which files need to be modified, created, or deleted",
                    "Break down the changes into clear, sequential steps",
                    "Do NOT provide full code implementations unless required by tools",
                    "Keep the plan concise and actionable",
                ]
            ),
            Leaves.OperatingPrinciples(),
        ]

    def get_context_template(self):
        return [
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
                    " > ERROR: The workflow has incomplete phases, you MUST use the provided tools to complete the workflow."
                )
