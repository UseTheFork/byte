from byte.core.command.registry import Command


class ExitCommand(Command):
    @property
    def name(self) -> str:
        return "exit"

    @property
    def description(self) -> str:
        return "Exit ByteSmith"

    async def execute(self, args: str) -> str:
        # This will be handled specially in the main loop
        return "EXIT_REQUESTED"


class HelpCommand(Command):
    @property
    def name(self) -> str:
        return "help"

    @property
    def description(self) -> str:
        return "Show available commands"

    async def execute(self, args: str) -> str:
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
