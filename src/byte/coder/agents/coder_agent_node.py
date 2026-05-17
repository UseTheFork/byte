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
from byte.support import Section, SectionType, Str


class CoderAgentNode(BaseAgentNode):
    def boot(
        self,
        goto: Type[BaseNode] = EndNode,
        **kwargs,
    ):
        """
        Initialize the CoderAgentNode with a target node to route to after execution.

        Args:
            goto: The target node class to route to after the agent completes. Defaults to EndNode.
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        self.goto = Str.class_to_snake_case(goto)

    def get_model(self) -> tuple[ModelSchema, dict]:
        llm_service = self.app.make(LLMService)
        return llm_service.get_model(self.name)

    def get_user_template(self):
        return [
            Leaves.ConversationHistory(),
            Leaves.UserRequest(),
            Section.important(
                f"All tool operations are applied immediately and are reflected in the next user message containing {Section.ref(SectionType.PROJECT_FILES)}."
            ),
        ]

    def get_system_template(self):
        return [
            Leaves.Preamble(role="Act as an expert software developer."),
            Leaves.Constitution(),
            Leaves.SkillsAvailable(),
            Leaves.CommunicationStyle(
                [
                    "   - Under 4 lines of text (tool use doesn't count)",
                    "   - Conciseness is about **text only**: always fully implement the requested feature, tests, and wiring even if that requires many tool calls.",
                    "   - No explanations unless user asks",
                    "   - Never send acknowledgement-only responses; after receiving new context or instructions, immediately continue the task or state the concrete next action you will take.",
                ]
            ),
            Leaves.WorkflowConstraints(
                [
                    "   - Analyze the user's request and the provided file context",
                    "   - If the request is ambiguous, ask clarifying questions",
                    "   - Identify which files need to be modified, created, or deleted",
                    "   - Break down the changes into clear, sequential steps",
                    "   - Do NOT provide full code implementations unless required by tools",
                    "   - Keep the plan concise and actionable",
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
                record_response_service.record_response(prompt, self.name, config),  # ty:ignore[invalid-argument-type]
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

        # msg = extract_content_from_message(result)
        # return self.route_to(self.goto, {"scratch_messages": AIMessage(content=msg, agent_name=self.name)})
