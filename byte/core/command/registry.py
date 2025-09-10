from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from rich.console import Console


class Command(ABC):
    """Base class for all commands."""

    def __init__(self, container=None):
        self.container = container

    @property
    @abstractmethod
    def name(self) -> str:
        """Command name (without prefix)."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Command description for help."""
        pass

    @abstractmethod
    async def execute(self, args: str) -> str:
        """Execute the command with given arguments."""
        pass

    def get_completions(self, text: str) -> List[str]:
        """Return completion suggestions for this command."""
        return []

    def pre_prompt(self, console: Console) -> None:
        """Display information before the prompt. Override to show status."""
        pass


class CommandRegistry:
    def __init__(self):
        self._slash_commands: Dict[str, Command] = {}
        self._at_commands: Dict[str, Command] = {}

    def register_slash_command(self, command: Command):
        """Register a slash command."""
        self._slash_commands[command.name] = command

    def get_slash_command(self, name: str) -> Optional[Command]:
        return self._slash_commands.get(name)

    def get_at_command(self, name: str) -> Optional[Command]:
        return self._at_commands.get(name)

    def pre_prompt(self, console: Console) -> None:
        """Display pre-prompt info from all registered commands."""
        for command in self._slash_commands.values():
            command.pre_prompt(console)

    def get_slash_completions(self, text: str) -> List[str]:
        """Get completions for slash commands."""
        if not text.startswith("/"):
            return []

        text = text[1:]  # Remove /
        if " " not in text:
            # Complete command names
            return [
                f"/{cmd}" for cmd in self._slash_commands.keys() if cmd.startswith(text)
            ]
        else:
            # Complete command arguments
            cmd_name, args = text.split(" ", 1)
            command = self._slash_commands.get(cmd_name)
            if command:
                return command.get_completions(args)
        return []

    def get_at_completions(self, text: str) -> List[str]:
        """Get completions for @ commands."""
        if not text.startswith("@"):
            return []

        text = text[1:]  # Remove @
        if " " not in text:
            # Complete command names
            return [
                f"@{cmd}" for cmd in self._at_commands.keys() if cmd.startswith(text)
            ]
        else:
            # Complete command arguments
            cmd_name, args = text.split(" ", 1)
            command = self._at_commands.get(cmd_name)
            if command:
                return command.get_completions(args)
        return []


# Global registry
command_registry = CommandRegistry()
