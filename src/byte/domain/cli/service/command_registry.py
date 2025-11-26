import argparse
from abc import ABC, abstractmethod
from argparse import Namespace
from typing import Dict, List, Optional

from byte.core.mixins.bootable import Bootable
from byte.core.mixins.configurable import Configurable
from byte.core.mixins.injectable import Injectable
from byte.core.mixins.user_interactive import UserInteractive
from byte.core.service.base_service import Service
from byte.domain.cli.argparse.base import ByteArgumentParser
from byte.domain.cli.service.console_service import ConsoleService


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
    def category(self) -> str:
        """Category for grouping in documentation.

        Override to organize commands into specific categories in generated docs.
        Usage: return "File Management" for file-related commands
        """
        return "General"

    @property
    def description(self) -> str:
        """Human-readable description for help system.

        By default, extracts description from the argument parser.
        Can be overridden for custom descriptions.
        """
        parser: ByteArgumentParser = self.parser
        return parser.description or "No description available"

    @property
    @abstractmethod
    def parser(self) -> ByteArgumentParser:
        """Get the argument parser for this command.

        Override to define command-specific arguments. The parser's description
        will be used for help text and documentation generation.

        Usage: Override in subclass to add arguments
        """
        pass

    async def handle(self, args: str) -> None:
        """Parse and execute the command with the provided arguments.

        Parses the raw argument string using the command's parser, handles
        any parsing errors by displaying usage information, and executes
        the command with the parsed arguments.

        Args:
            args: Raw argument string from user input

        Usage: Called by CommandRegistry when command is invoked
        """
        parser = self.parser

        try:
            parsed_args = parser.parse_args(args.split() if args else [])
        except argparse.ArgumentError:
            console = await self.make(ConsoleService)
            console.print_error_panel(parser.format_help(), title="Invalid Command Arguments")
            return

        return await self.execute(parsed_args, args)

    @abstractmethod
    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Execute the command with provided arguments.

        Args:
            args: Parsed arguments from the argument parser
            raw_args: Raw argument string for commands that need custom parsing

        Commands can choose to use either parsed args or raw_args depending on their needs.
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
            return [f"{cmd}" for cmd in self._slash_commands.keys() if cmd.startswith(text)]
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
            return [f"@{cmd}" for cmd in self._at_commands.keys() if cmd.startswith(text)]
        else:
            # Delegate argument completion to specific command
            cmd_name, args = text.split(" ", 1)
            command = self._at_commands.get(cmd_name)
            if command:
                return await command.get_completions(args)
        return []
