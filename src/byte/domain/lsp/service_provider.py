from typing import List, Type

from byte.container import Container
from byte.core.config.config import ByteConfg
from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.cli.service.command_registry import Command
from byte.domain.lsp.service.lsp_service import LSPService


class LSPServiceProvider(ServiceProvider):
	"""Service provider for Language Server Protocol integration.

	Registers LSP services for multi-language code intelligence features
	like hover information, references, definitions, and completions.
	Usage: Register with container to enable LSP functionality
	"""

	def services(self) -> List[Type[Service]]:
		"""Return list of LSP services to register."""
		return [LSPService]

	def commands(self) -> List[Type[Command]]:
		"""Return list of LSP commands to register."""
		return []

	async def boot(self, container: Container):
		""""""
		config = await container.make(ByteConfg)
		if config.lsp.enable:
			# Boots the LSPs and starts them in the background.
			await container.make(LSPService)

	async def shutdown(self, container: Container) -> None:
		"""Shutdown all LSP servers gracefully."""
		config = await container.make(ByteConfg)
		if config.lsp.enable:
			lsp_service = await container.make(LSPService)
			await lsp_service.shutdown_all()
