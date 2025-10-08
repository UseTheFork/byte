from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from byte.core.utils import get_last_message
from byte.domain.agent.implementations.base import Agent
from byte.domain.agent.implementations.research.prompts import research_prompt
from byte.domain.agent.nodes.assistant_node import AssistantNode
from byte.domain.agent.nodes.end_node import EndNode
from byte.domain.agent.nodes.start_node import StartNode
from byte.domain.agent.nodes.tool_node import ToolNode
from byte.domain.agent.state import BaseState
from byte.domain.llm.service.llm_service import LLMService
from byte.domain.mcp.service.mcp_service import MCPService
from byte.domain.tools.read_file import read_file
from byte.domain.tools.ripgrep_search import ripgrep_search


class ResearchAgent(Agent):
    """Domain service for AI-powered code research and information gathering.

    Extends Agent to provide research capabilities with tool execution for
    file searching and reading. Integrates with MCP services for extended
    tool availability and uses ripgrep for fast codebase searches.
    Usage: `agent = await container.make(ResearchAgent); result = await agent.execute(state)`
    """

    async def boot(self):
        pass

    def get_tools(self):
        return [ripgrep_search, read_file]

    async def build(self) -> CompiledStateGraph:
        """Build and compile the coder agent graph with memory and tools."""

        # Create the assistant and runnable
        llm_service = await self.make(LLMService)
        llm: BaseChatModel = llm_service.get_main_model()
        assistant_runnable = research_prompt | llm.bind_tools(self.get_tools())

        mcp_service = await self.make(MCPService)
        mcp_tools = mcp_service.get_tools_for_agent("research")

        # Create the state graph
        graph = StateGraph(self.get_state_class())

        # Add nodes
        graph.add_node(
            "start",
            await self.make(
                StartNode,
                agent=self.__class__.__name__,
            ),
        )

        graph.add_node(
            "assistant",
            await self.make(AssistantNode, runnable=assistant_runnable),
        )
        graph.add_node(
            "tools", await self.make(ToolNode, tools=[*self.get_tools(), *mcp_tools])
        )

        graph.add_node(
            "end",
            await self.make(
                EndNode,
                agent=self.__class__.__name__,
                llm=llm,
            ),
        )

        # Define edges
        graph.add_edge(START, "start")
        graph.add_edge("start", "assistant")
        graph.add_edge("assistant", "end")

        # Conditional routing from assistant
        graph.add_conditional_edges(
            "assistant",
            self.route_tools,
            {"tools": "tools", "end": "end"},
        )

        graph.add_edge("tools", "assistant")
        graph.add_edge("end", END)

        return graph.compile()

    def route_tools(
        self,
        state: BaseState,
    ):
        """
        Use in the conditional_edge to route to the ToolNode if the last message
        has tool calls. Otherwise, route to the end.
        """
        ai_message = get_last_message(state)

        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"
        return "end"
