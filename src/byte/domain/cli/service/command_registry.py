from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from byte.core.mixins.bootable import Bootable
from byte.core.mixins.configurable import Configurable
from byte.core.mixins.injectable import Injectable
from byte.core.mixins.user_interactive import UserInteractive
from byte.core.service.base_service import Service


class Command(ABC, Bootable, Injectable, Configurable, UserInteractive):
    """Base class for all commands implementing the Command pattern.

    Provides a consistent interface for executable commands with support for
    tab completion, help text, and pre-prompt status display.
    Usage: `class MyCommand(Command): ...` then register with CommandRegistry
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Command name used for invocation (without prefix).

        Usage: return "add" for /add command
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description for help system.

        Should briefly explain what the command does and basic usage.
        """
        pass

    @abstractmethod
    async def execute(self, args: str) -> None:
        """Execute the command with provided arguments.

        Args contain everything after the command name, unparsed.
        Commands should handle their own argument parsing and validation.
        """
        pass

    async def get_completions(self, text: str) -> List[str]:
        """Return tab completion suggestions for command arguments.

        Override to provide context-aware completions like file paths.
        Usage: return ["file1.py", "file2.py"] for file path completions
        """
        return []


class CommandRegistry(Service):
    """Central registry for command discovery and routing.

    Manages command registration and provides lookup services for both
    slash commands (/add) and @ commands (@mention). Supports tab completion
    for improved user experience.
    """

    async def boot(self):
        # Separate namespaces for different command types
        self._slash_commands: Dict[str, Command] = {}
        self._at_commands: Dict[str, Command] = {}

    async def register_slash_command(self, command: Command):
        """Register a slash command for /command syntax.

        Usage: `await registry.register_slash_command(AddFileCommand())`
        """
        self._slash_commands[command.name] = command

    def get_slash_command(self, name: str) -> Optional[Command]:
        """Retrieve a registered slash command by name."""
        return self._slash_commands.get(name)

    def get_at_command(self, name: str) -> Optional[Command]:
        """Retrieve a registered @ command by name."""
        return self._at_commands.get(name)

    async def get_slash_completions(self, text: str) -> List[str]:
        """Generate tab completions for slash commands and their arguments.

        Handles both command name completion and argument completion by
        delegating to individual command completion handlers.
        """
        if not text.startswith("/"):
            return []

        text = text[1:]  # Remove /
        if " " not in text:
            # Complete command names when no space present
            return [
                f"{cmd}" for cmd in self._slash_commands.keys() if cmd.startswith(text)
            ]
        else:
            # Delegate argument completion to specific command
            cmd_name, args = text.split(" ", 1)
            command = self._slash_commands.get(cmd_name)
            if command:
                return await command.get_completions(args)
        return []

    async def get_at_completions(self, text: str) -> List[str]:
        """Generate tab completions for @ commands and their arguments.

        Similar to slash completions but for @command syntax.
        """
        if not text.startswith("@"):
            return []

        text = text[1:]  # Remove @
        if " " not in text:
            # Complete command names when no space present
            return [
                f"@{cmd}" for cmd in self._at_commands.keys() if cmd.startswith(text)
            ]
        else:
            # Delegate argument completion to specific command
            cmd_name, args = text.split(" ", 1)
            command = self._at_commands.get(cmd_name)
            if command:
                return await command.get_completions(args)
        return []
