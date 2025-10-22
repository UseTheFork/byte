from typing import List, Type

from byte.container import Container
from byte.core.event_bus import EventBus, EventType
from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.cli.service.command_registry import Command
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.memory.command.undo_command import UndoCommand
from byte.domain.system.command.exit_command import ExitCommand
from byte.domain.system.command.initilizie_command import InitilizieCommand
from byte.domain.system.service.system_context_service import SystemContextService


class SystemServiceProvider(ServiceProvider):
	"""Service provider for system-level commands and functionality.

	Registers core system commands like exit and help, making them available
	through the command registry for user interaction via slash commands.
	Usage: Register with container to enable /exit and /help commands
	"""

	def commands(self) -> List[Type[Command]]:
		return [
			ExitCommand,
			InitilizieCommand,
			UndoCommand,
		]

	def services(self) -> List[Type[Service]]:
		return [
			SystemContextService,
		]

	async def boot(self, container: "Container") -> None:
		"""Boot system services and register commands with registry.

		Usage: `provider.boot(container)` -> commands become available as /exit, /help
		"""

		event_bus = await container.make(EventBus)
		system_context_service = await container.make(SystemContextService)

		event_bus.on(
			EventType.GATHER_PROJECT_CONTEXT.value,
			system_context_service.add_system_context,
		)

		console = await container.make(ConsoleService)

		console.print("│ ", style="text")
		console.rule("╰─── //")
