from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from byte.domain.agent.implementations.ask.prompts import ask_prompt
from byte.domain.agent.implementations.base import Agent
from byte.domain.agent.nodes.assistant_node import AssistantNode
from byte.domain.agent.nodes.setup_node import SetupNode
from byte.domain.agent.state import AskState
from byte.domain.llm.service.llm_service import LLMService
from byte.domain.mcp.service.mcp_service import MCPService


class AskAgent(Agent):
    """"""

    def get_state_class(self):
        """Return coder-specific state class."""
        return AskState

    async def build(self):
        """ """

        mcp_service = await self.make(MCPService)
        mcp_tools = mcp_service.get_tools_for_agent("ask")

        # Create the assistant and runnable
        llm_service = await self.make(LLMService)
        llm: BaseChatModel = llm_service.get_main_model()
        assistant_runnable = ask_prompt | llm.bind_tools(mcp_tools)

        # Create the state graph
        graph = StateGraph(self.get_state_class())

        # Add nodes
        graph.add_node("setup", await self.make(SetupNode))
        graph.add_node(
            "assistant", await self.make(AssistantNode, runnable=assistant_runnable)
        )
        graph.add_node("tools", ToolNode(mcp_tools))

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
        return graph.compile()

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
