from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langgraph.constants import END
from langgraph.graph import START, StateGraph
from rich.markdown import Markdown

from byte.core.mixins.user_interactive import UserInteractive
from byte.domain.agent.implementations.base import Agent
from byte.domain.agent.implementations.cleaner.prompt import cleaner_prompt
from byte.domain.agent.nodes.assistant_node import AssistantNode
from byte.domain.agent.nodes.end_node import EndNode
from byte.domain.agent.nodes.start_node import StartNode
from byte.domain.agent.schemas import AssistantRunnable
from byte.domain.agent.state import CleanerState
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.llm.service.llm_service import LLMService


class CleanerAgent(Agent, UserInteractive):
	"""Domain service for extracting relevant information from content.

	Processes raw content to extract only essential information for services
	like session context, removing noise and focusing on key details.
	Usage: `agent = await container.make(CleanerAgent); clean = await agent.execute(state)`
	"""

	def get_state_class(self):
		"""Return cleaner-specific state class.

		Usage: `state_class = agent.get_state_class()`
		"""
		return CleanerState

	async def build(self):
		"""Build and compile the cleaner agent graph.

		Creates a StateGraph optimized for content cleaning with specialized
		prompts focused on information extraction and relevance filtering.
		Usage: `graph = await agent.build()` -> ready for content cleaning
		"""
		assistant_runnable = await self.get_assistant_runnable()

		# Create the state graph
		graph = StateGraph(self.get_state_class())

		# Add nodes
		graph.add_node(
			"start",
			await self.make(StartNode, agent=self.__class__.__name__),
		)

		graph.add_node(
			"assistant",
			await self.make(AssistantNode, runnable=assistant_runnable.runnable),
		)

		graph.add_node(
			"end",
			await self.make(
				EndNode,
				agent=self.__class__.__name__,
				llm=assistant_runnable.llm,
			),
		)

		graph.add_node("extract_clean_content", self._extract_clean_content)
		graph.add_node("confirm_content", self._confirm_content)

		# Define edges
		graph.add_edge(START, "start")
		graph.add_edge("start", "assistant")
		graph.add_edge("assistant", "extract_clean_content")
		graph.add_edge("extract_clean_content", "confirm_content")

		# Conditional routing after extraction - ask user to confirm or modify
		graph.add_conditional_edges(
			"confirm_content",
			self._route_after_extraction,
			{
				"confirm": "end",
				"retry": "assistant",
			},
		)

		graph.add_edge("end", END)

		# Compile graph without memory for stateless operation
		return graph.compile()

	def _extract_clean_content(self, state: CleanerState):
		"""Extract cleaned content from assistant response and update state.

		Usage: `result = agent._extract_clean_content(state)` -> {"cleaned_content": "..."}
		"""
		messages = state["messages"]
		last_message = messages[-1]

		return {"cleaned_content": last_message.content}

	async def _confirm_content(self, state: CleanerState):
		"""Ask user to confirm the cleaned content or provide modifications.

		Displays the extracted content and prompts user to either accept it
		or provide feedback for modification.
		Usage: `result = await agent._confirm_content(state)` -> updated state
		"""

		console = await self.make(ConsoleService)

		cleaned_content = state.get("cleaned_content", "")

		markdown_rendered = Markdown(cleaned_content)
		console.print(
			console.panel(
				markdown_rendered,
				title="Cleaned Content",
			)
		)

		confirmed, user_input = await self.prompt_for_confirm_or_input(
			"Use this cleaned content?",
			"Please provide instructions for how to modify the content:",
			default_confirm=True,
		)

		if confirmed:
			# User accepted the content, proceed to end
			return {"user_confirmed": True}
		else:
			# User wants modifications, add their feedback to messages
			messages = list(state.get("messages", []))
			messages.append(
				HumanMessage(content=f"Please revise the cleaned content based on this feedback: {user_input}")
			)
			return {
				"messages": messages,
				"user_confirmed": False,
			}

	def _route_after_extraction(self, state: CleanerState):
		"""Route based on whether user has confirmed the content.

		Returns "confirm" to proceed to confirmation node, or "retry" if
		user has provided modification feedback.
		Usage: `route = agent._route_after_extraction(state)` -> "confirm" or "retry"
		"""
		# Check if we've already been through confirmation
		if state.get("user_confirmed") is not None:
			if state.get("user_confirmed"):
				return "confirm"
			else:
				return "retry"

		# First time through, go to confirmation
		return "confirm"

	async def get_assistant_runnable(self) -> AssistantRunnable:
		llm_service = await self.make(LLMService)
		llm: BaseChatModel = llm_service.get_weak_model()

		return AssistantRunnable(
			runnable=cleaner_prompt | llm,
			llm=llm,
		)
