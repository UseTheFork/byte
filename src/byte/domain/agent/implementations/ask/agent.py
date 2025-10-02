from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import END, START, StateGraph

from byte.domain.agent.implementations.ask.prompts import ask_prompt
from byte.domain.agent.implementations.base import Agent
from byte.domain.agent.nodes.assistant_node import AssistantNode
from byte.domain.agent.nodes.setup_node import SetupNode
from byte.domain.agent.nodes.tool_node import ToolNode
from byte.domain.agent.state import AskState
from byte.domain.llm.service.llm_service import LLMService
from byte.domain.mcp.service.mcp_service import MCPService


class AskAgent(Agent):
    """Domain service for the ask agent specialized in question answering with tools.

    Pure domain service that handles query processing and tool execution without
    UI concerns. Integrates with MCP tools and the LLM service through the actor
    system for clean separation of concerns.

    Usage: `agent = await container.make(AskAgent); response = await agent.run(state)`
    """

    def get_state_class(self):
        """Return ask-specific state class.

        Usage: `state_class = agent.get_state_class()`
        """
        return AskState

    async def build(self):
        """Build and compile the ask agent graph with memory and MCP tools.

        Creates a graph workflow that processes user queries through setup,
        assistant, and tool execution nodes with conditional routing based
        on whether tool calls are required.

        Usage: `graph = await agent.build()`
        """

        mcp_service = await self.make(MCPService)
        mcp_tools = mcp_service.get_tools_for_agent("ask")

        # Create the assistant and runnable
        llm_service = await self.make(LLMService)
        llm: BaseChatModel = llm_service.get_main_model()
        assistant_runnable = ask_prompt | llm.bind_tools(mcp_tools)

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
        graph.add_node("tools", await self.make(ToolNode, tools=mcp_tools))

        # Define edges
        graph.add_edge(START, "setup")
        graph.add_edge("setup", "assistant")
        graph.add_edge("assistant", END)

        graph.add_conditional_edges(
            "assistant",
            self.route_tools,
            {"tools": "tools", END: END},
        )

        graph.add_edge("tools", "assistant")

        # Compile graph with memory and configuration
        checkpointer = await self.get_checkpointer()
        return graph.compile(checkpointer=checkpointer, debug=False)

    def route_tools(
        self,
        state: AskState,
    ):
        """
        Use in the conditional_edge to route to the ToolNode if the last message
        has tool calls. Otherwise, route to the end.
        """
        if isinstance(state, list):
            ai_message = state[-1]
        elif messages := state.get("messages", []):
            ai_message = messages[-1]
        else:
            raise ValueError(f"No messages found in input state to tool_edge: {state}")

        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"
        return END
