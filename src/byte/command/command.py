import argparse
from abc import ABC, abstractmethod
from argparse import Namespace
from typing import List

from byte import ByteArgumentParser
from byte.support.mixins import Bootable, Eventable, Notifiable, UserInteractive


class Command(ABC, Bootable, UserInteractive, Notifiable, Eventable):
    """Base class for all commands implementing the Command pattern."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provide the command name used for invocation."""
        pass

    @property
    def category(self) -> str:
        """Provide the category for grouping in documentation."""
        return "General"

    @property
    def description(self) -> str:
        """Provide a human-readable description for the help system."""
        parser: ByteArgumentParser = self.parser
        return parser.description or "No description available"

    @property
    @abstractmethod
    def parser(self) -> ByteArgumentParser:
        """Provide the argument parser for this command."""
        pass

    async def handle(self, args: str) -> None:
        """Parse and execute the command with provided arguments.

        Args:
            args: Raw argument string to parse.
        """
        parser = self.parser

        try:
            parsed_args = parser.parse_args(args.split() if args else [])
        except argparse.ArgumentError:
            console = self.app["console"]
            console.print_error_panel(parser.format_help(), title="Invalid Command Arguments")
            return

        return await self.execute(parsed_args, args)

    @abstractmethod
    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Execute the command with provided arguments.

        Args:
            args: Parsed arguments from the argument parser.
            raw_args: Raw argument string before parsing.
        """
        pass

    async def get_completions(self, text: str) -> List[str]:
        """Provide tab completion suggestions for command arguments."""
        return []
