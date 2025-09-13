from typing import TYPE_CHECKING, Optional

from byte.core.command.registry import Command

if TYPE_CHECKING:
    from byte.container import Container


class ExitCommand(Command):
    """Command to gracefully exit the ByteSmith application.

    Returns a special signal that the main loop recognizes to terminate
    the application cleanly, allowing for proper cleanup operations.
    Usage: `/exit` -> triggers application shutdown
    """

    def __init__(self, container: Optional["Container"] = None):
        super().__init__(container)

    @property
    def name(self) -> str:
        return "exit"

    @property
    def description(self) -> str:
        return "Exit ByteSmith"

    async def execute(self, args: str) -> str:
        """Signal application exit to the main loop.

        Usage: Called by command processor when user types `/exit`
        """
        return "EXIT_REQUESTED"


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

    async def execute(self, args: str) -> str:
        """Generate formatted help text for all registered commands.

        Usage: Called by command processor when user types `/help`
        """
        if not self.container:
            return "Help system not available"

        command_registry = self.container.make("command_registry")
        slash_commands = command_registry._slash_commands

        help_text = "Available commands:\n\n"

        if slash_commands:
            help_text += "Slash commands:\n"
            for name, cmd in slash_commands.items():
                help_text += f"  /{name} - {cmd.description}\n"
            help_text += "\n"

        return help_text.strip()
