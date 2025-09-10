from byte.commands.registry import Command, command_registry


class HelpCommand(Command):
    @property
    def name(self) -> str:
        return "help"

    @property
    def description(self) -> str:
        return "Show available commands"

    async def execute(self, args: str) -> str:
        slash_commands = command_registry._slash_commands

        help_text = "Available commands:\n\n"

        if slash_commands:
            help_text += "Slash commands:\n"
            for name, cmd in slash_commands.items():
                help_text += f"  /{name} - {cmd.description}\n"
            help_text += "\n"

        return help_text.strip()


# Auto-register
command_registry.register_slash_command(HelpCommand())
