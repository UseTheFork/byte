from typing import List, Type

from rich.console import Console

from byte.container import Container
from byte.core.actors.base import Actor
from byte.core.service_provider import ServiceProvider
from byte.domain.cli_input.actor.input_actor import InputActor
from byte.domain.system.actor.coordinator_actor import CoordinatorActor
from byte.domain.system.actor.system_command_actor import SystemCommandActor


class SystemServiceProvider(ServiceProvider):
    """Service provider for system-level commands and functionality.

    Registers core system commands like exit and help, making them available
    through the command registry for user interaction via slash commands.
    Usage: Register with container to enable /exit and /help commands
    """

    def actors(self) -> List[Type[Actor]]:
        return [CoordinatorActor, SystemCommandActor]

    async def register(self, container: "Container") -> None:
        """Register system commands in the container.

        Usage: `provider.register(container)` -> binds exit and help commands
        """
        # container.bind(ExitCommand)
        # container.bind(HelpCommand)
        # container.bind(AddFileCommand)
        # container.bind(ReadOnlyCommand)
        # container.bind(DropFileCommand)

    async def boot(self, container: "Container") -> None:
        """Boot system services and register commands with registry.

        Usage: `provider.boot(container)` -> commands become available as /exit, /help
        """

        input_actor = await container.make(InputActor)

        await input_actor.register_command_handler("exit", SystemCommandActor)
        await input_actor.register_command_handler("help", SystemCommandActor)

        # # Register system commands for user access
        # await command_registry.register_slash_command(await container.make(ExitCommand))
        # await command_registry.register_slash_command(await container.make(HelpCommand))

        # # Set up PrePrompt event listeners for file commands
        # add_file_command = await container.make(AddFileCommand)
        # readonly_command = await container.make(ReadOnlyCommand)
        # drop_file_command = await container.make(DropFileCommand)

        # # Register file commands with the command registry
        # await command_registry.register_slash_command(add_file_command)
        # await command_registry.register_slash_command(readonly_command)
        # await command_registry.register_slash_command(drop_file_command)

        # # event_dispatcher.listen(PrePrompt, self._handle_pre_prompt)

        # # Store command references for event handling
        # self._add_file_command = add_file_command
        # self._readonly_command = readonly_command

        console = await container.make(Console)

        console.print("│", style="text")
        console.print("┕─[success]LETS GOOOO!![/success]")
