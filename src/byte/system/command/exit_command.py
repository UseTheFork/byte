from argparse import Namespace

from byte import ByteArgumentParser, Command
from byte.tui import TUIManagerService


class ExitCommand(Command):
    """Exit the Byte application gracefully."""

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
        """Exit the application by signaling the TUI manager."""
        tui_manager_service = self.app.make(TUIManagerService)
        tui_manager_service.exit()
