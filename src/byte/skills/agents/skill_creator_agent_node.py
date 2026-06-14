from typing import Literal

from langgraph.graph.state import RunnableConfig
from langgraph.types import Command

from byte.node import (
    BaseAgentNode,
)
from byte.orchestration import BaseState, Leaves, PhaseUtils


class SkillCreatorAgentNode(BaseAgentNode):
    llm_tier: str = "reasoning"

    def get_user_template(self):
        return [
            Leaves.HarnessInstruction(),
        ]

    def get_system_template(self):
        return [
            Leaves.Preamble(
                role="Act as an expert skill creator. Your job is to help users design and create skills by understanding their intent, asking the right questions, and producing clear, well-structured skill definitions."
            ),
            Leaves.CommunicationStyle(
                verbose=True,
            ),
            Leaves.WorkflowConstraints(
                [
                    "- Understand what the user wants the skill to do before writing anything",
                    "- If the request is ambiguous, ask clarifying questions about intent, expected output, and when the skill should trigger",
                    "- Capture the skill's name, description, and instructions before creating it",
                    "- FIRST gather the necessary information, THEN use available tools to create the skill",
                    "- Keep skill instructions clear, concise, and actionable",
                ]
            ),
        ]

    def get_context_template(self):
        return [
            Leaves.Constitution(),
            Leaves.ProjectEnvironment(),
            Leaves.HarnessWorkspaceReferenceContext(),
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
