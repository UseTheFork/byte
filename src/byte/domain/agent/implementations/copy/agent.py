from typing import Type

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from typing_extensions import TypedDict

from byte.domain.agent.implementations.base import Agent
from byte.domain.agent.nodes.copy_node import CopyNode
from byte.domain.agent.state import CoderState


class CopyAgent(Agent):
	"""Agent for extracting and copying code blocks from messages.

	Provides an interactive workflow to select and copy code blocks from
	the last AI response to the system clipboard using pyperclip.
	Usage: Invoked via `/copy` command in the CLI
	"""

	def get_state_class(self) -> Type[TypedDict]:  # pyright: ignore[reportInvalidTypeForm]
		"""Return coder-specific state class."""
		return CoderState

	async def build(self) -> CompiledStateGraph:
		"""Build and compile the coder agent graph with memory and tools."""

		# Create the state graph
		graph = StateGraph(self.get_state_class())

		# Add nodes
		graph.add_node(
			"copy_node",
			await self.make(CopyNode),
		)

		# Define edges
		graph.add_edge(START, "copy_node")
		graph.add_edge("copy_node", END)

		checkpointer = await self.get_checkpointer()
		return graph.compile(checkpointer=checkpointer, debug=False)

	async def get_assistant_runnable(self) -> None:
		pass
