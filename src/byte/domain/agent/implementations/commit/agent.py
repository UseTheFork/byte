from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.constants import END
from langgraph.graph import START, StateGraph

from byte.domain.agent.implementations.base import Agent
from byte.domain.agent.implementations.commit.prompt import commit_prompt
from byte.domain.agent.nodes.assistant_node import AssistantNode
from byte.domain.agent.nodes.end_node import EndNode
from byte.domain.agent.nodes.extract_node import ExtractNode
from byte.domain.agent.nodes.start_node import StartNode
from byte.domain.agent.schemas import AssistantContextSchema
from byte.domain.agent.state import BaseState
from byte.domain.llm.service.llm_service import LLMService


class CommitAgent(Agent):
    """Domain service for generating AI-powered git commit messages and creating commits."""

    async def build(self):
        """Build and compile the coder agent graph with memory and tools.

        Creates a StateGraph optimized for coding tasks with specialized
        prompts, file context integration, and development-focused routing.
        Usage: `graph = await builder.build()` -> ready for coding assistance
        """

        # Create the state graph
        graph = StateGraph(BaseState)

        # Add nodes
        graph.add_node("start_node", await self.make(StartNode))
        graph.add_node("extract_node", await self.make(ExtractNode))
        graph.add_node("assistant_node", await self.make(AssistantNode, goto="extract_node"))
        graph.add_node("end_node", await self.make(EndNode))

        # Define edges
        graph.add_edge(START, "start_node")
        graph.add_edge("start_node", "assistant_node")
        graph.add_edge("assistant_node", "extract_node")
        graph.add_edge("extract_node", "end_node")
        graph.add_edge("end_node", END)

        # Compile graph with memory and configuration
        return graph.compile()

    async def get_assistant_runnable(self) -> AssistantContextSchema:
        llm_service = await self.make(LLMService)
        main: BaseChatModel = llm_service.get_main_model()
        weak: BaseChatModel = llm_service.get_weak_model()

        return AssistantContextSchema(
            mode="weak",
            prompt=commit_prompt,
            main=main,
            weak=weak,
            agent=self.__class__.__name__,
        )
