from typing import Literal

from langgraph.graph.state import RunnableConfig
from langgraph.types import Command

from byte.development import RecordResponseService
from byte.node import (
    BaseAgentNode,
)
from byte.orchestration import BaseState, Leaves, PhaseUtils
from byte.support import Section, SectionType


class SpecTaskCreatorAgentNode(BaseAgentNode):
    def get_user_template(self):
        return [
            Leaves.Spec(),
        ]

    def get_system_template(self):
        return [
            Leaves.Preamble(
                role="Act as an expert spec creator. Write or complete a comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste."
            ),
            Leaves.Constitution(),
            Leaves.OperatingPrinciples(),
            Leaves.CommunicationStyle(verbose=True),
            Leaves.WorkflowConstraints(
                [
                    "Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, how to test it.",
                    "Assume they are a skilled developer, but know almost nothing about our toolset or problem domain.",
                ]
            ),
            Section.start(SectionType.TEMPLATE),
            "Use this template when creating tasks",
            "```",
            "# [Feature Name] Implementation Plan",
            "**Goal:** [One sentence describing what this builds]",
            "**Architecture:** [2-3 sentences about approach]",
            "---",
            "[Task Instruction]",
            "```",
            Section.end(),
        ]

    def get_context_template(self):
        return [
            Leaves.SpecTasks(),
            Leaves.ReferenceMaterials(),
            Leaves.ProjectEnvironment(),
            Leaves.HarnessWorkspaceFiles(),
            Leaves.HarnessWorkspaceReferenceFiles(),
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
        record_response_service = self.app.make(RecordResponseService)
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
