import os

from byte.container import Container
from byte.core.service_provider import ServiceProvider
from byte.domain.cli.service.command_registry import CommandRegistry
from byte.domain.development.command.test_command import TestCommand


class DevelopmentProvider(ServiceProvider):
	"""Service provider specifically for various dev tools."""

	async def register(self, container: Container):
		# Only bind these if we are running in dev mode.
		if os.getenv("BYTE_DEV_MODE", "").lower() in ("true", "1", "yes"):
			container.bind(TestCommand)

	async def boot(self, container: Container):
		# Only bind these if we are running in dev mode.
		if os.getenv("BYTE_DEV_MODE", "").lower() in ("true", "1", "yes"):
			command_registry = await container.make(CommandRegistry)

			test_command = await container.make(TestCommand)
			await command_registry.register_slash_command(test_command)
