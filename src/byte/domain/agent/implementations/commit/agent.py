from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.constants import END
from langgraph.graph import START, StateGraph

from byte.domain.agent.implementations.base import Agent
from byte.domain.agent.implementations.commit.prompt import commit_prompt
from byte.domain.agent.nodes.assistant_node import AssistantNode
from byte.domain.agent.nodes.setup_node import SetupNode
from byte.domain.agent.state import CommitState
from byte.domain.llm.service.llm_service import LLMService


class CommitAgent(Agent):
    """Domain service for generating AI-powered git commit messages and creating commits."""

    def get_state_class(self):
        """Return coder-specific state class."""
        return CommitState

    async def build(self):
        """Build and compile the coder agent graph with memory and tools.

        Creates a StateGraph optimized for coding tasks with specialized
        prompts, file context integration, and development-focused routing.
        Usage: `graph = await builder.build()` -> ready for coding assistance
        """

        llm_service = await self.make(LLMService)
        llm: BaseChatModel = llm_service.get_weak_model()
        assistant_runnable = commit_prompt | llm

        # Create the state graph
        graph = StateGraph(self.get_state_class())

        # Add nodes
        graph.add_node(
            "setup",
            await self.make(SetupNode, agent=self.__class__.__name__),
        )
        graph.add_node(
            "assistant",
            await self.make(AssistantNode, runnable=assistant_runnable),
        )

        graph.add_node("extract_commit", self._extract_commit)

        # Define edges
        graph.add_edge(START, "assistant")
        graph.add_edge("assistant", "extract_commit")
        graph.add_edge("extract_commit", END)

        # Compile graph with memory and configuration
        return graph.compile()

    def _extract_commit(self, state: CommitState):
        """Extract commit message from assistant response and update state.

        Usage: `result = agent._extract_commit(state)` -> {"commit_message": "fix: ..."}
        """
        messages = state["messages"]
        last_message = messages[-1]

        return {"commit_message": last_message.content}
