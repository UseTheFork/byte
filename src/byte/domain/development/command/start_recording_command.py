from rich.console import Console

from byte.core.config.config import ByteConfg
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

		config = await self.make(ByteConfg)
		console = await self.make(Console)
		console.save_svg(str(config.project_root / "docs" / "images" / "test.svg"), title="")
		# raise KeyboardInterrupt
