from byte.container import Container
from byte.core.service_provider import ServiceProvider
from byte.domain.files.commands import AddFileCommand, DropFileCommand, ReadOnlyCommand
from byte.domain.files.context_manager import FileContextManager
from byte.domain.files.repository import InMemoryFileRepository
from byte.domain.files.service import FileService


class FileServiceProvider(ServiceProvider):
    """Service provider for all file-related functionality."""

    def register(self, container: Container):
        """Register file services and commands."""
        # Register core file services
        container.singleton("file_context_manager", lambda: FileContextManager())
        container.bind("file_repository", lambda: InMemoryFileRepository())
        container.bind(
            "file_service",
            lambda: FileService(
                container.make("file_repository"),
                container.make("file_context_manager"),
            ),
        )

        # Register file-related commands
        container.bind("add_file_command", lambda: AddFileCommand(container))
        container.bind("readonly_command", lambda: ReadOnlyCommand(container))
        container.bind("drop_file_command", lambda: DropFileCommand(container))

    def boot(self, container: Container):
        """Boot file services and register commands with registry."""
        # Get the command registry
        command_registry = container.make("command_registry")

        # Register all file-related commands
        command_registry.register_slash_command(container.make("add_file_command"))
        command_registry.register_slash_command(container.make("readonly_command"))
        command_registry.register_slash_command(container.make("drop_file_command"))

    def provides(self) -> list:
        return [
            "file_repository",
            "file_service",
            "add_file_command",
            "readonly_command",
            "drop_file_command",
        ]
