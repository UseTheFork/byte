from typing import Literal

from langgraph.graph.state import RunnableConfig
from langgraph.types import Command

from byte.git import CommitService
from byte.node import (
    BaseAgentNode,
)
from byte.orchestration import BaseState, Leaves, PhaseUtils
from byte.support import Section

# Conventional commit message generation prompt
# Adapted from Aider: https://github.com/Aider-AI/aider/blob/e4fc2f515d9ed76b14b79a4b02740cf54d5a0c0b/aider/prompts.py#L8
# Conventional Commits specification: https://www.conventionalcommits.org/en/v1.0.0/#summary


class CommitAgentNode(BaseAgentNode):
    def get_user_template(self):
        return [
            Leaves.GitDiffs(),
            Leaves.ConversationHistory(),
            Leaves.CommitHistory(),
            "",
        ]

    def get_system_template(self):
        return [
            Leaves.Preamble(
                "You are an expert software engineer that generates organized Git commits based on the provided user input."
            ),
            Leaves.CommunicationStyle(
                extra_styles=[
                    "Conciseness is about **text only**: always fully implement the requested feature, tests, and wiring even if that requires many tool calls.",
                    "No explanations unless user asks",
                    "Never send acknowledgement-only responses; after receiving new context or instructions, immediately continue the task or state the concrete next action you will take.",
                ]
            ),
            Section.end(),
            Leaves.OperatingPrinciples(),
            Leaves.CommitGuidelines(),
        ]

    def get_context_template(self):
        return [
            Leaves.ToolsLoaded(),
            Leaves.WorkflowPending(),
            Leaves.Epilogue(),
        ]

    async def __call__(
        self,
        state: BaseState,
        *,
        config: RunnableConfig,
    ) -> Command[Literal["routing_node"]]:

        commit_service = self.app.make(CommitService)
        request = await commit_service.build_commit_prompt()

        prompt_assembler = await self.generate_agent_state(state, config, request)
        runnable = self.create_runnable(prompt_assembler)
        prompt = await self.generate_prompt(prompt_assembler)

        while True:
            result = await runnable.ainvoke(prompt, config=config)
            await self.finalize_response(result, prompt, config)

            route_tool_call = self.route_tool_calls(result)
            if route_tool_call is not None:
                return route_tool_call

            if not PhaseUtils.is_workflow_complete(prompt_assembler.get_state()):
                prompt[-1].content[0]["text"] += (  # ty:ignore[invalid-argument-type]
                    " > ERROR: The workflow has incomplete phases, you MUST use the provided tools to complete the workflow."
                )
