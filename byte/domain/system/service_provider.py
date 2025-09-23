from typing import List, Type

from rich.console import Console

from byte.container import Container
from byte.core.actors.base import Actor
from byte.core.service_provider import ServiceProvider
from byte.domain.cli_input.service.command_registry import Command
from byte.domain.system.actor.coordinator_actor import CoordinatorActor
from byte.domain.system.command.exit_command import ExitCommand


class SystemServiceProvider(ServiceProvider):
    """Service provider for system-level commands and functionality.

    Registers core system commands like exit and help, making them available
    through the command registry for user interaction via slash commands.
    Usage: Register with container to enable /exit and /help commands
    """

    def actors(self) -> List[Type[Actor]]:
        return [CoordinatorActor]

    def commands(self) -> List[Type[Command]]:
        return [ExitCommand]

    async def boot(self, container: "Container") -> None:
        """Boot system services and register commands with registry.

        Usage: `provider.boot(container)` -> commands become available as /exit, /help
        """

        console = await container.make(Console)

        console.print("│", style="text")
        console.print("┕─[success]LETS GOOOO!![/success]")
