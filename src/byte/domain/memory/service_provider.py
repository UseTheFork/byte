from typing import TYPE_CHECKING, List, Type

from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.cli.service.command_registry import Command
from byte.domain.memory.command.clear_command import ClearCommand
from byte.domain.memory.command.reset_command import ResetCommand
from byte.domain.memory.service.memory_service import MemoryService

if TYPE_CHECKING:
	from byte.container import Container


class MemoryServiceProvider(ServiceProvider):
	"""Service provider for conversation memory management.

	Registers memory services for short-term conversation persistence using
	LangGraph checkpointers. Enables stateful conversations and thread
	management for the AI agent system.
	Usage: Register with container to enable conversation memory
	"""

	def services(self) -> List[Type[Service]]:
		return [MemoryService]

	def commands(self) -> List[Type[Command]]:
		return [ClearCommand, ResetCommand]

	async def shutdown(self, container: "Container"):
		"""Shutdown memory services and close database connections."""
		try:
			if MemoryService in container._instances:
				memory_service = await container.make(MemoryService)
				await memory_service.close()
		except Exception:
			pass  # Ignore cleanup errors during shutdown
