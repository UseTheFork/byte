from byte.container import Container
from byte.core.service_provider import ServiceProvider
from byte.domain.files.commands import AddFileCommand, DropFileCommand, ReadOnlyCommand
from byte.domain.files.context_manager import FileContextManager
from byte.domain.files.repository import InMemoryFileRepository
from byte.domain.files.service import FileService


class FileServiceProvider(ServiceProvider):
    """Service provider for all file-related functionality."""

    async def register(self, container: Container):
        """Register file services and commands."""
        # Register core file services
        container.singleton("file_context_manager", lambda: FileContextManager())
        container.bind("file_repository", lambda: InMemoryFileRepository())

        # Register file service with async factory
        async def create_file_service():
            file_repository = await container.make("file_repository")
            file_context_manager = await container.make("file_context_manager")
            return FileService(file_repository, file_context_manager)

        container.bind("file_service", create_file_service)

        # Register file-related commands
        container.bind("add_file_command", lambda: AddFileCommand(container))
        container.bind("readonly_command", lambda: ReadOnlyCommand(container))
        container.bind("drop_file_command", lambda: DropFileCommand(container))

    async def boot(self, container: Container):
        """Boot file services and register commands with registry."""
        # Get the command registry
        command_registry = await container.make("command_registry")

        # Register all file-related commands
        await command_registry.register_slash_command(
            await container.make("add_file_command")
        )
        await command_registry.register_slash_command(
            await container.make("readonly_command")
        )
        await command_registry.register_slash_command(
            await container.make("drop_file_command")
        )

    def provides(self) -> list:
        return [
            "file_repository",
            "file_service",
            "add_file_command",
            "readonly_command",
            "drop_file_command",
        ]
