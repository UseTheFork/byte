from langchain_core.messages import HumanMessage
from langgraph.graph.message import RemoveMessage
from langgraph.graph.state import RunnableConfig

from byte.domain.agent.implementations.coder.agent import CoderAgent
from byte.domain.cli.service.command_registry import Command
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.memory.service.memory_service import MemoryService


class UndoCommand(Command):
	"""Undo the last conversation step by rolling back to previous checkpoint.

	Reverts the conversation state to the previous checkpoint, effectively
	undoing the last user message and agent response in the current thread.
	"""

	@property
	def name(self) -> str:
		return "undo"

	@property
	def category(self) -> str:
		return "Memory"

	@property
	def description(self) -> str:
		return "Undo the last conversation step by removing the most recent human message and all subsequent agent responses from the current thread"

	async def execute(self, args: str) -> None:
		"""Execute undo operation on current conversation thread.

		Usage: `/undo` -> reverts to previous checkpoint state
		"""
		memory_service = await self.make(MemoryService)
		console = await self.make(ConsoleService)

		# It dosent matter if we use CoderAgent or AskAgent here since they use the same BaseState.
		coder_agent = await self.make(CoderAgent)
		coder_agent_graph = await coder_agent.get_graph()

		memory_service = await self.make(MemoryService)
		thread_id = await memory_service.get_or_create_thread()

		config = RunnableConfig(configurable={"thread_id": thread_id})
		state_snapshot = await coder_agent_graph.aget_state(config)
		messages = state_snapshot.values.get("messages", [])

		# Find the most recent HumanMessage index
		last_human_index = None
		for i in range(len(messages) - 1, -1, -1):
			if isinstance(messages[i], HumanMessage):
				last_human_index = i
				break

		# Get all messages from the most recent HumanMessage onwards
		if last_human_index is not None:
			messages_to_remove = messages[last_human_index:]
			remove_messages = [RemoveMessage(id=message.id) for message in messages_to_remove]

			# Count messages by type
			message_counts = {}
			for message in messages_to_remove:
				message_type = type(message).__name__
				message_counts[message_type] = message_counts.get(message_type, 0) + 1

			# Display message counts in a panel
			count_text = "\n".join([f"{msg_type}: {count}" for msg_type, count in message_counts.items()])
			num_messages = len(messages_to_remove)
			console.print_panel(
				count_text,
				title="Messages to Remove",
			)

			confirmed = console.confirm(
				f"Remove {num_messages} message{'s' if num_messages != 1 else ''}?", default=True
			)

			if confirmed:
				await coder_agent_graph.aupdate_state(config, {"messages": remove_messages})

				console.print_success_panel(
					"Successfully undone last step",
					title="Undo",
				)
