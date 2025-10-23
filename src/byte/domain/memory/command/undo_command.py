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
	def description(self) -> str:
		return "Undo the last conversation step"

	async def execute(self, args: str) -> None:
		"""Execute undo operation on current conversation thread.

		Usage: `/undo` -> reverts to previous checkpoint state
		"""
		memory_service = await self.make(MemoryService)
		console = await self.make(ConsoleService)

		success = await memory_service.undo_last_step()

		if success:
			console.print_success_panel(
				"Successfully undone last step",
				title="Undo",
			)
		else:
			console.print_error_panel(
				"Cannot undo: no previous checkpoint available",
				title="Undo Failed",
			)
