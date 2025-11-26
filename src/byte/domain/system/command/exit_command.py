from argparse import Namespace

from byte.domain.cli.argparse.base import ByteArgumentParser
from byte.domain.cli.service.command_registry import Command


class ExitCommand(Command):
    """Command to gracefully shutdown the Byte application.

    Sends a shutdown message to the coordinator actor to initiate
    a clean application exit with proper resource cleanup.
    Usage: `/exit` -> terminates the application
    """

    @property
    def name(self) -> str:
        return "exit"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Exit the Byte application gracefully",
        )
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Execute the exit command by sending shutdown message to coordinator."""
        raise KeyboardInterrupt
