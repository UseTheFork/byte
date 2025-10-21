import asyncio

from rich.console import Console

from byte.bootstrap import bootstrap, shutdown
from byte.container import Container
from byte.context import container_context
from byte.core.cli import cli
from byte.core.config.config import ByteConfg
from byte.core.logging import log
from byte.core.task_manager import TaskManager
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.cli.service.prompt_toolkit_service import PromptToolkitService


class Byte:
	"""Main application class that orchestrates the CLI interface and command processing.

	Separates concerns by delegating prompt handling to PromptHandler and command
	processing to CommandProcessor, while maintaining the main event loop.
	"""

	def __init__(self, container: Container):
		self.container = container
		self.actor_tasks = []

	async def initialize(self):
		"""Discover and start all registered actors"""
		# Get all registered actor instances

		self.task_manager = await self.container.make(TaskManager)

	async def run(self):
		""" """
		await self.initialize()
		try:
			await self._main_loop()
		finally:
			await self.task_manager.shutdown()

	async def _main_loop(self):
		"""Main application loop - easy to follow"""
		input_service = await self.container.make(PromptToolkitService)

		while True:
			try:
				# Get user input (this can be async/non-blocking)
				await input_service.execute()
			except KeyboardInterrupt:
				break
			except Exception as e:
				log.exception(e)
				console = await self.container.make(ConsoleService)
				console.print_error_panel(
					str(e),
					title="Exception",
				)
				# console.console.print_exception(show_locals=True)


async def main(config: ByteConfg):
	"""Application entry point"""
	container = await bootstrap(config)
	container_context.set(container)

	# Create and run the actor-based app
	app = Byte(container)
	await app.run()

	# Cleanup
	await shutdown(container)

	console = Console()
	console.print("[warning]Goodbye![/warning]")


def run(config: ByteConfg):
	asyncio.run(main(config))


if __name__ == "__main__":
	cli()
