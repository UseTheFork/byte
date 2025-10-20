from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import END, START, StateGraph

from byte.domain.agent.implementations.ask.prompts import ask_prompt
from byte.domain.agent.implementations.base import Agent
from byte.domain.agent.nodes.assistant_node import AssistantNode
from byte.domain.agent.nodes.end_node import EndNode
from byte.domain.agent.nodes.start_node import StartNode
from byte.domain.agent.nodes.tool_node import ToolNode
from byte.domain.agent.schemas import AssistantRunnable
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

		assistant_runnable = await self.get_assistant_runnable()

		# Create the state graph
		graph = StateGraph(self.get_state_class())

		# Add nodes
		graph.add_node(
			"start_node",
			await self.make(StartNode, agent=self.__class__.__name__),
		)
		graph.add_node(
			"assistant_node",
			await self.make(AssistantNode, runnable=assistant_runnable.runnable),
		)
		graph.add_node("tools_node", await self.make(ToolNode, tools=assistant_runnable.tools))  # pyright: ignore[reportArgumentType]

		graph.add_node(
			"end_node",
			await self.make(
				EndNode,
				agent=self.__class__.__name__,
				llm=assistant_runnable.llm,
			),
		)

		# Define edges
		graph.add_edge(START, "start_node")
		graph.add_edge("start_node", "assistant_node")
		graph.add_edge("assistant_node", "end_node")
		graph.add_edge("end_node", END)

		graph.add_edge("tools_node", "assistant_node")

		# Compile graph with memory and configuration
		checkpointer = await self.get_checkpointer()
		return graph.compile(checkpointer=checkpointer)

	async def get_assistant_runnable(self) -> AssistantRunnable:
		llm_service = await self.make(LLMService)
		llm: BaseChatModel = llm_service.get_main_model()

		mcp_service = await self.make(MCPService)
		mcp_tools = mcp_service.get_tools_for_agent("ask")

		# Create the assistant runnable with out any tools. So regardless it wont make a tool call even thou we have a tool node.
		return AssistantRunnable(
			runnable=ask_prompt | llm.bind_tools(mcp_tools, parallel_tool_calls=False),
			llm=llm,
			tools=mcp_tools,
		)
