from rich.console import Console

from byte.domain.cli.service.command_registry import Command


class StartRecordingCommand(Command):
	""" """

	@property
	def name(self) -> str:
		return "dev:rec:start"

	@property
	def description(self) -> str:
		return ""

	async def execute(self, args: str) -> None:
		""" """
		console = await self.make(Console)
		console.record = True
