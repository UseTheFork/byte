from byte.container import Container
from byte.core.service_provider import ServiceProvider
from byte.domain.system.commands import ExitCommand, HelpCommand


class SystemServiceProvider(ServiceProvider):
    """Service provider for system-level commands and functionality."""

    def register(self, container: Container):
        """Register system commands in the container."""

        # Register system commands
        container.bind("exit_command", lambda: ExitCommand(container))
        container.bind("help_command", lambda: HelpCommand(container))

    def boot(self, container: Container):
        """Boot system services and register commands with registry."""
        # Get the command registry
        command_registry = container.make("command_registry")

        # Register all system commands
        command_registry.register_slash_command(container.make("exit_command"))
        command_registry.register_slash_command(container.make("help_command"))

    def provides(self) -> list:
        return [
            "exit_command",
            "help_command",
        ]
