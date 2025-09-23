from typing import List, Type

from rich.console import Console

from byte.container import Container
from byte.core.actors.base import Actor
from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.cli_input.service.command_registry import Command
from byte.domain.files.actor.file_actor import FileActor
from byte.domain.files.command.add_file_command import AddFileCommand
from byte.domain.files.command.add_read_only_file_command import ReadOnlyCommand
from byte.domain.files.command.drop_file_command import DropFileCommand
from byte.domain.files.command.list_files_command import ListFilesCommand
from byte.domain.files.service.discovery_service import FileDiscoveryService
from byte.domain.files.service.file_service import FileService
from byte.domain.files.service.watcher_service import FileWatcherService


class FileServiceProvider(ServiceProvider):
    """Service provider for simplified file functionality with project discovery."""

    def actors(self) -> List[Type[Actor]]:
        return [FileActor]

    def services(self) -> List[Type[Service]]:
        return [FileDiscoveryService, FileService, FileWatcherService]

    def commands(self) -> List[Type[Command]]:
        return [ListFilesCommand, AddFileCommand, ReadOnlyCommand, DropFileCommand]

    async def boot(self, container: Container):
        """Boot file services and register commands with registry."""
        # Ensure file discovery is booted first to scan project files
        file_discovery = await container.make(FileDiscoveryService)
        await file_discovery.ensure_booted()

        console = await container.make(Console)

        found_files = await file_discovery.get_files()
        console.print(
            f"├─ [success]Discovered:[/success] [info]{len(found_files)} files[/info]"
        )
        console.print("│", style="text")
