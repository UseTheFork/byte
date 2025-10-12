from typing import List, Type

from byte.container import Container
from byte.core.event_bus import EventBus, EventType
from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.cli.service.command_registry import Command
from byte.domain.edit_format.command.copy_command import CopyCommand
from byte.domain.edit_format.service.edit_block_service import EditBlockService
from byte.domain.edit_format.service.edit_format_service import EditFormatService
from byte.domain.edit_format.service.shell_command_service import ShellCommandService


class EditFormatProvider(ServiceProvider):
	"""Service provider for edit format and code block processing functionality.

	Registers services for parsing and applying SEARCH/REPLACE blocks and shell
	commands from AI responses. Manages the edit block lifecycle and integrates
	with the event system for message preprocessing.
	Usage: Register with container to enable edit format processing
	"""

	def services(self) -> List[Type[Service]]:
		return [EditFormatService]

	def commands(self) -> List[Type[Command]]:
		return [CopyCommand]

	async def register(self, container: "Container"):
		"""Register edit block and shell command services in the container.

		Binds non-singleton services that handle parsing, validating, and
		executing SEARCH/REPLACE blocks and shell commands from AI responses.
		Usage: Called during provider registration phase
		"""
		container.bind(EditBlockService)
		container.bind(ShellCommandService)

	async def boot(self, container: Container):
		"""Boot edit services and register event listeners for message preprocessing.

		Initializes the edit block service and registers an event listener that
		replaces edit blocks in historic messages with their applied results
		before passing context to the AI agent.
		Usage: Called during provider boot phase
		"""
		edit_format_service = await container.make(EditBlockService)

		event_bus = await container.make(EventBus)
		event_bus.on(
			EventType.PRE_ASSISTANT_NODE.value,
			edit_format_service.replace_blocks_in_historic_messages_hook,
		)
