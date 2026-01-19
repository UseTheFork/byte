from langchain_core.language_models.chat_models import BaseChatModel

from byte.agent import (
    Agent,
    AssistantContextSchema,
    AssistantNode,
    ValidationNode,
)
from byte.agent.implementations.commit.prompt import commit_prompt
from byte.git import CommitMessage, CommitPlan, CommitValidator
from byte.llm import LLMService


class CommitAgent(Agent):
    """Domain service for generating AI-powered git commit messages and creating commits."""

    def get_validators(self):
        return [
            self.app.make(CommitValidator),
        ]

    def get_structured_output(self):
        return CommitMessage

    async def build(self):
        """Build and compile the coder agent graph with memory and tools.

        Creates a StateGraph optimized for coding tasks with specialized
        prompts, file context integration, and development-focused routing.
        Usage: `graph = await builder.build()` -> ready for coding assistance
        """

        graph = self.get_base_graph(
            [
                "tools_node",
                "extract_node",
                "subprocess_node",
                "parse_blocks_node",
            ],
        )

        graph.add_node(
            "assistant_node",
            self.app.make(AssistantNode, goto="validation_node", structured_output=self.get_structured_output()),  # ty:ignore[invalid-argument-type]
        )

        graph.add_node(
            "validation_node",
            self.app.make(
                ValidationNode,
                goto="end_node",
                validators=self.get_validators(),
            ),  # ty:ignore[invalid-argument-type]
        )

        # Compile graph with memory and configuration
        return graph.compile()

    async def get_assistant_runnable(self) -> AssistantContextSchema:
        llm_service = self.app.make(LLMService)
        main: BaseChatModel = llm_service.get_main_model()
        weak: BaseChatModel = llm_service.get_weak_model()

        return AssistantContextSchema(
            mode="weak",
            prompt=commit_prompt,
            main=main,
            weak=weak,
            agent=self.__class__.__name__,
        )


class CommitPlanAgent(CommitAgent):
    """Domain service for generating AI-powered git commit messages and creating commits."""

    def get_validators(self):
        return [
            self.app.make(CommitValidator),
        ]

    def get_structured_output(self):
        return CommitPlan
