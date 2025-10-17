from typing import List

from byte.domain.cli.service.command_registry import Command
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.knowledge.service.session_context_service import SessionContextService


class ContextDropCommand(Command):
	"""Command to remove items from session context.

	Enables users to clean up session context by removing items that are no
	longer relevant, reducing noise and improving AI focus on current task.
	Usage: `/context:drop item_key` -> removes item from session context
	"""

	@property
	def name(self) -> str:
		return "context:drop"

	@property
	def description(self) -> str:
		return "Remove item from session context"

	async def execute(self, args: str) -> None:
		"""Remove specified item from session context."""
		console = await self.make(ConsoleService)
		if not args:
			console.print("Usage: /context:drop <context_key>")
			return

		session_context_service = await self.make(SessionContextService)
		context_items = session_context_service.get_all_context()

		if args in context_items:
			session_context_service.remove_context(args)
			console.print(f"[success]Removed {args} from session context[/success]")
			return
		else:
			console.print(f"[error]Context item {args} not found[/error]")
			return

	async def get_completions(self, text: str) -> List[str]:
		"""Provide intelligent context key completions.

		Suggests existing context keys that match the input pattern.
		"""
		try:
			session_context_service = await self.make(SessionContextService)
			context_items = session_context_service.get_all_context()

			# Filter keys that start with the input text
			matches = [key for key in context_items.keys() if key.startswith(text)]
			return matches
		except Exception:
			return []
