from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from byte.domain.agent.implementations.base import Agent
from byte.domain.agent.implementations.research.prompt import research_prompt
from byte.domain.agent.nodes.assistant_node import AssistantNode
from byte.domain.agent.nodes.end_node import EndNode
from byte.domain.agent.nodes.extract_node import ExtractNode
from byte.domain.agent.nodes.start_node import StartNode
from byte.domain.agent.nodes.tool_node import ToolNode
from byte.domain.agent.schemas import AssistantContextSchema
from byte.domain.agent.state import BaseState
from byte.domain.llm.service.llm_service import LLMService
from byte.domain.lsp.tools.find_references import find_references
from byte.domain.lsp.tools.get_definition import get_definition
from byte.domain.lsp.tools.get_hover_info import get_hover_info


class ResearchAgent(Agent):
    """Domain service for AI-powered code research and information gathering.

    Extends Agent to provide research capabilities with tool execution for
    file searching and reading. Integrates with MCP services for extended
    tool availability and uses ripgrep for fast codebase searches.
    Usage: `agent = await container.make(ResearchAgent); result = await agent.execute(state)`
    """

    # Research agent dosent use or update the main memory even thou it gets the current checkpointer state.
    async def get_checkpointer(self):
        return None

    def get_tools(self):
        return [find_references, get_definition, get_hover_info]
        # return [ripgrep_search, read_file]

    async def build(self) -> CompiledStateGraph:
        """Build and compile the coder agent graph with memory and tools."""

        # Create the assistant and runnable
        graph = StateGraph(BaseState)

        # Add nodes
        graph.add_node("start_node", await self.make(StartNode))
        graph.add_node("assistant_node", await self.make(AssistantNode, goto="extract_node"))
        graph.add_node("extract_node", await self.make(ExtractNode, schema="session_context"))
        graph.add_node("tools_node", await self.make(ToolNode))

        graph.add_node("end_node", await self.make(EndNode))

        # Define edges
        graph.add_edge(START, "start_node")
        graph.add_edge("start_node", "assistant_node")

        graph.add_edge("extract_node", "end_node")

        graph.add_edge("end_node", END)

        graph.add_edge("tools_node", "assistant_node")

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.compile(checkpointer=checkpointer)

    async def get_assistant_runnable(self) -> AssistantContextSchema:
        llm_service = await self.make(LLMService)
        main: BaseChatModel = llm_service.get_main_model()
        weak: BaseChatModel = llm_service.get_weak_model()

        return AssistantContextSchema(
            mode="main",
            prompt=research_prompt,
            main=main,
            weak=weak,
            agent=self.__class__.__name__,
            tools=self.get_tools(),
        )
