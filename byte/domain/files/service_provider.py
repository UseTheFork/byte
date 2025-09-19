from byte.container import Container
from byte.core.command.registry import CommandRegistry
from byte.core.service_provider import ServiceProvider
from byte.domain.files.commands import AddFileCommand, DropFileCommand, ReadOnlyCommand
from byte.domain.files.discovery_service import FileDiscoveryService
from byte.domain.files.service import FileService


class FileServiceProvider(ServiceProvider):
    """Service provider for simplified file functionality with project discovery."""

    async def register(self, container: Container):
        """Register file services and commands."""

        # Register file discovery service as singleton for caching
        container.singleton(FileDiscoveryService)
        container.singleton(FileService)

        # Register file-related commands
        container.bind(AddFileCommand)
        container.bind(ReadOnlyCommand)
        container.bind(DropFileCommand)

    async def boot(self, container: Container):
        """Boot file services and register commands with registry."""
        # Ensure file discovery is booted first to scan project files
        file_discovery = await container.make(FileDiscoveryService)
        await file_discovery.ensure_booted()

        # Get the command registry
        command_registry = await container.make(CommandRegistry)

        # Register all file-related commands
        await command_registry.register_slash_command(
            await container.make(AddFileCommand)
        )
        await command_registry.register_slash_command(
            await container.make(ReadOnlyCommand)
        )
        await command_registry.register_slash_command(
            await container.make(DropFileCommand)
        )

    def provides(self) -> list:
        return [
            FileDiscoveryService,
            FileService,
            AddFileCommand,
            ReadOnlyCommand,
            DropFileCommand,
        ]
