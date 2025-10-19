from byte import dd
from byte.domain.cli.service.command_registry import Command
from byte.domain.cli.service.console_service import ConsoleService


class TestCommand(Command):
	""" """

	@property
	def name(self) -> str:
		return "dev:test"

	@property
	def description(self) -> str:
		return ""

	async def execute(self, args: str) -> None:
		""" """
		console = await self.make(ConsoleService)

		menu = console.select(
			"Option 1",
			"Option 2",
			"Option 3",
			"Option 4",
			"Option 5",
			"Option 6",
			"Option 7",
			"Option 8",
			"Option 9",
			"Exit",
			title="test",
		)
		dd(menu)
