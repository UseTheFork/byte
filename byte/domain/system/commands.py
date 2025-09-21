from typing import TYPE_CHECKING, Optional

from rich.console import Console

from byte.core.actors.message import Message, MessageBus, MessageType
from byte.core.command.registry import Command, CommandRegistry
from byte.core.logging import log
from byte.domain.events.mixins import Eventable
from byte.domain.system.actor.coordinator_actor import CoordinatorActor

if TYPE_CHECKING:
    from byte.container import Container


class ExitCommand(Command, Eventable):
    """Command to gracefully exit the Byte application.

    Emits ExitRequested event that the main loop listens for to terminate
    the application cleanly, allowing for proper cleanup operations.
    Usage: `/exit` -> triggers application shutdown
    """

    @property
    def name(self) -> str:
        return "exit"

    @property
    def description(self) -> str:
        return "Exit Byte"

    async def execute(self, args: str) -> None:
        """Emit exit event to signal application shutdown.

        Usage: Called by command processor when user types `/exit`
        """
        log.info("1234243243243")
        message_bus = await self.make(MessageBus)
        await message_bus.send_to(
            CoordinatorActor,
            Message(
                type=MessageType.SHUTDOWN,
                payload={"reason": "user_exit_command"},
            ),
        )


class HelpCommand(Command):
    """Command to display available system commands and their descriptions.

    Dynamically generates help text by querying the command registry,
    ensuring the help output stays current as commands are added or removed.
    Usage: `/help` -> shows all available slash commands
    """

    def __init__(self, container: Optional["Container"] = None):
        super().__init__(container)

    @property
    def name(self) -> str:
        return "help"

    @property
    def description(self) -> str:
        return "Show available commands"

    async def execute(self, args: str) -> None:
        """Display formatted help text for all registered commands.

        Usage: Called by command processor when user types `/help`
        """
        if not self.container:
            console = self.container.make("console") if self.container else None
            if console:
                console.print("[error]Help system not available[/error]")
            return

        command_registry = await self.container.make(CommandRegistry)
        console = await self.container.make(Console)
        slash_commands = command_registry._slash_commands

        help_text = "Available commands:\n\n"

        if slash_commands:
            help_text += "Slash commands:\n"
            for name, cmd in slash_commands.items():
                help_text += f"  /{name} - {cmd.description}\n"
            help_text += "\n"

        console.print(help_text.strip())
