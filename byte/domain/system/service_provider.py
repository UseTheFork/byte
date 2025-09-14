from typing import TYPE_CHECKING

from byte.container import Container
from byte.core.service_provider import ServiceProvider
from byte.domain.system.commands import ExitCommand, HelpCommand

if TYPE_CHECKING:
    from byte.container import Container


class SystemServiceProvider(ServiceProvider):
    """Service provider for system-level commands and functionality.

    Registers core system commands like exit and help, making them available
    through the command registry for user interaction via slash commands.
    Usage: Register with container to enable /exit and /help commands
    """

    async def register(self, container: "Container") -> None:
        """Register system commands in the container.

        Usage: `provider.register(container)` -> binds exit and help commands
        """
        container.bind("exit_command", lambda: ExitCommand(container))
        container.bind("help_command", lambda: HelpCommand(container))

    async def boot(self, container: "Container") -> None:
        """Boot system services and register commands with registry.

        Usage: `provider.boot(container)` -> commands become available as /exit, /help
        """
        command_registry = await container.make("command_registry")

        # Register system commands for user access
        await command_registry.register_slash_command(
            await container.make("exit_command")
        )
        await command_registry.register_slash_command(
            await container.make("help_command")
        )

    def provides(self) -> list:
        """Return list of services provided by this provider."""
        return [
            "exit_command",
            "help_command",
        ]
