from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import END, START, StateGraph

from byte.domain.agent.implementations.ask.prompts import ask_prompt
from byte.domain.agent.implementations.base import Agent
from byte.domain.agent.nodes.assistant_node import AssistantNode
from byte.domain.agent.nodes.setup_node import SetupNode
from byte.domain.agent.state import AskState
from byte.domain.llm.service.llm_service import LLMService


class AskAgent(Agent):
    """"""

    def get_state_class(self):
        """Return coder-specific state class."""
        return AskState

    async def build(self):
        """ """

        # Create the assistant and runnable
        llm_service = await self.make(LLMService)
        llm: BaseChatModel = llm_service.get_main_model()
        assistant_runnable = ask_prompt | llm

        # Create the state graph
        graph = StateGraph(self.get_state_class())

        # Add nodes
        graph.add_node("setup", await self.make(SetupNode))
        graph.add_node(
            "assistant", await self.make(AssistantNode, runnable=assistant_runnable)
        )

        # Define edges
        graph.add_edge(START, "setup")
        graph.add_edge("setup", "assistant")
        graph.add_edge("assistant", END)

        # Compile graph with memory and configuration
        return graph.compile()
