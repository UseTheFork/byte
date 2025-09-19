from typing import TYPE_CHECKING

from byte.container import Container
from byte.core.command.registry import CommandRegistry
from byte.core.service_provider import ServiceProvider
from byte.domain.events.dispatcher import EventDispatcher
from byte.domain.files.commands import AddFileCommand, DropFileCommand, ReadOnlyCommand
from byte.domain.system.commands import ExitCommand, HelpCommand
from byte.domain.system.events import PrePrompt

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
        container.singleton(AddFileCommand)
        container.singleton(ReadOnlyCommand)
        container.singleton(DropFileCommand)

    async def boot(self, container: "Container") -> None:
        """Boot system services and register commands with registry.

        Usage: `provider.boot(container)` -> commands become available as /exit, /help
        """
        command_registry = await container.make(CommandRegistry)
        event_dispatcher = await container.make(EventDispatcher)

        # Register system commands for user access
        await command_registry.register_slash_command(await container.make(ExitCommand))
        await command_registry.register_slash_command(await container.make(HelpCommand))

        # Set up PrePrompt event listeners for file commands
        add_file_command = await container.make(AddFileCommand)
        readonly_command = await container.make(ReadOnlyCommand)
        drop_file_command = await container.make(DropFileCommand)

        # Register file commands with the command registry
        await command_registry.register_slash_command(add_file_command)
        await command_registry.register_slash_command(readonly_command)
        await command_registry.register_slash_command(drop_file_command)

        event_dispatcher.listen("PrePrompt", self._handle_pre_prompt)

        # Store command references for event handling
        self._add_file_command = add_file_command
        self._readonly_command = readonly_command

    async def _handle_pre_prompt(self, event: PrePrompt) -> None:
        """Handle PrePrompt events by calling pre_prompt methods on file commands.

        This allows file commands to display contextual information before each prompt.
        """
        # Call pre_prompt methods on file commands to display context
        await self._add_file_command.pre_prompt()
        await self._readonly_command.pre_prompt()

    def provides(self) -> list:
        """Return list of services provided by this provider."""
        return [
            ExitCommand,
            HelpCommand,
            AddFileCommand,
            ReadOnlyCommand,
            DropFileCommand,
        ]
