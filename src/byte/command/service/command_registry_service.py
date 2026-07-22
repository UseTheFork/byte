from typing import Dict, List, Optional

from byte import Command
from byte.support import Service


class CommandRegistryService(Service):
    """Manage command registration and provide lookup services for slash and @ commands."""

    def boot(self):
        # Separate namespaces for different command types
        self._slash_commands: Dict[str, Command] = {}

    def register_slash_command(self, command: Command):
        """Register a slash command for /command syntax."""
        self._slash_commands[command.name] = command

    def get_slash_command(self, name: str) -> Optional[Command]:
        """Retrieve a registered slash command by name."""
        return self._slash_commands.get(name)

    def get_all_commands(self) -> List[Command]:
        """Retrieve all registered commands (both slash and @ commands)."""
        all_commands = list(self._slash_commands.values())
        return all_commands

    def get_all_slash_command_names(self) -> List[str]:
        """Retrieve all registered slash command names prefixed with /."""
        return [f"/{name}" for name in self._slash_commands.keys()]

    async def get_slash_completions(self, text: str) -> List[tuple[str, str]]:
        """Generate tab completions for slash commands and their arguments.

        Returns:
            Tuples of (completion_text, description) for matching commands or arguments.
        """
        if not text.startswith("/"):
            return []

        text = text[1:]  # Remove /
        if " " not in text:
            # Complete command names when no space present - return (name, description) tuples
            return [(cmd, command.description) for cmd, command in self._slash_commands.items() if cmd.startswith(text)]
        else:
            # Delegate argument completion to specific command
            cmd_name, args = text.split(" ", 1)
            command = self._slash_commands.get(cmd_name)
            if command:
                completions = await command.get_completions(args)
                # Return as tuples with empty descriptions for args
                return [(comp, "") for comp in completions]
        return []
