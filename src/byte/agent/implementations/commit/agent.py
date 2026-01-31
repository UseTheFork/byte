from langchain_core.language_models.chat_models import BaseChatModel

from byte.agent import (
    Agent,
    AssistantContextSchema,
    AssistantNode,
    EndNode,
    ValidationNode,
)
from byte.agent.implementations.commit.prompt import commit_enforcement, commit_prompt
from byte.agent.utils.graph_builder import GraphBuilder
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

        graph = GraphBuilder(self.app)

        # Add nodes
        graph.add_node(AssistantNode, goto=ValidationNode, structured_output=self.get_structured_output())
        graph.add_node(ValidationNode, goto=EndNode, validators=self.get_validators())

        return graph.build().compile()

        # Compile graph with memory and configuration
        return graph.compile()

    async def get_assistant_runnable(self) -> AssistantContextSchema:
        llm_service = self.app.make(LLMService)
        main: BaseChatModel = llm_service.get_main_model()
        weak: BaseChatModel = llm_service.get_weak_model()

        return AssistantContextSchema(
            mode="weak",
            prompt=commit_prompt,
            enforcement=self.get_enforcement(),
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

    def get_enforcement(self):
        return commit_enforcement

    def get_structured_output(self):
        return CommitPlan
