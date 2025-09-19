from typing import TYPE_CHECKING

from byte.container import Container
from byte.core.command.registry import CommandRegistry
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
        container.singleton(ExitCommand)
        container.singleton(HelpCommand)

    async def boot(self, container: "Container") -> None:
        """Boot system services and register commands with registry.

        Usage: `provider.boot(container)` -> commands become available as /exit, /help
        """
        command_registry = await container.make(CommandRegistry)

        # Register system commands for user access
        await command_registry.register_slash_command(await container.make(ExitCommand))
        await command_registry.register_slash_command(await container.make(HelpCommand))

    def provides(self) -> list:
        """Return list of services provided by this provider."""
        return [
            ExitCommand,
            HelpCommand,
        ]
