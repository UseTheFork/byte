from langgraph.graph.state import RunnableConfig
from langgraph.types import Command

from byte.core.mixins.user_interactive import UserInteractive
from byte.core.utils import extract_content_from_message, get_last_message
from byte.domain.agent.nodes.base_node import Node
from byte.domain.agent.state import BaseState


class ExtractNode(Node, UserInteractive):
	""" """

	async def boot(
		self,
		goto: str = "end_node",
		schema: str = "text",
		**kwargs,
	):
		self.schema = schema
		self.goto = goto

	async def __call__(self, state: BaseState, config: RunnableConfig):
		""""""
		last_message = get_last_message(state["messages"])

		if self.schema == "text":
			response_text = extract_content_from_message(last_message)
			return Command(goto=self.goto, update={"extracted_content": response_text})

		return Command(goto=self.goto, update={"extracted_content": ""})
