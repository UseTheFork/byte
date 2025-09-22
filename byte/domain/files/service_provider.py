from typing import List, Type

from rich.console import Console

from byte.container import Container
from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.files.service.discovery_service import FileDiscoveryService
from byte.domain.files.service.file_service import FileService
from byte.domain.files.service.watcher_service import FileWatcherService


class FileServiceProvider(ServiceProvider):
    """Service provider for simplified file functionality with project discovery."""

    def services(self) -> List[Type[Service]]:
        return [FileDiscoveryService, FileService, FileWatcherService]

    async def register(self, container: Container):
        """Register file services and commands."""
        pass

    async def boot(self, container: Container):
        """Boot file services and register commands with registry."""
        # Ensure file discovery is booted first to scan project files
        file_discovery = await container.make(FileDiscoveryService)
        await file_discovery.ensure_booted()

        # Boot the file watcher service (only if enabled in config)
        file_watcher = await container.make(FileWatcherService)
        await file_watcher.ensure_booted()

        # # Get the command registry
        # command_registry = await container.make(CommandRegistry)

        # # Register all file-related commands
        # await command_registry.register_slash_command(
        #     await container.make(AddFileCommand)
        # )
        # await command_registry.register_slash_command(
        #     await container.make(ReadOnlyCommand)
        # )
        # await command_registry.register_slash_command(
        #     await container.make(DropFileCommand)
        # )

        console = await container.make(Console)

        found_files = await file_discovery.get_files()
        console.print(
            f"├─ [success]Discovered:[/success] [info]{len(found_files)} files[/info]"
        )
        console.print("│", style="text")
