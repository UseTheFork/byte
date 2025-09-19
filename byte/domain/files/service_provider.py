from byte.container import Container
from byte.core.command.registry import CommandRegistry
from byte.core.service_provider import ServiceProvider
from byte.domain.events.dispatcher import EventDispatcher
from byte.domain.files.commands import AddFileCommand, DropFileCommand, ReadOnlyCommand
from byte.domain.files.discovery_service import FileDiscoveryService
from byte.domain.files.service import FileService
from byte.domain.files.watcher_service import FileWatcherService
from byte.domain.system.events import PrePrompt


class FileServiceProvider(ServiceProvider):
    """Service provider for simplified file functionality with project discovery."""

    async def register(self, container: Container):
        """Register file services and commands."""

        # Register file discovery service as singleton for caching
        container.singleton(FileDiscoveryService)
        container.singleton(FileService)
        container.singleton(FileWatcherService)

        # Register file-related commands
        container.bind(AddFileCommand)
        container.bind(ReadOnlyCommand)
        container.bind(DropFileCommand)

    async def boot(self, container: Container):
        """Boot file services and register commands with registry."""
        # Ensure file discovery is booted first to scan project files
        file_discovery = await container.make(FileDiscoveryService)
        await file_discovery.ensure_booted()

        # Boot the file watcher service (only if enabled in config)
        file_watcher = await container.make(FileWatcherService)
        await file_watcher.ensure_booted()

        # setup `PrePrompt` listener to display files in context
        file_service = await container.make(FileService)
        event_dispatcher = await container.make(EventDispatcher)
        event_dispatcher.listen(PrePrompt, file_service.list_in_context_files)

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
            FileWatcherService,
            AddFileCommand,
            ReadOnlyCommand,
            DropFileCommand,
        ]
