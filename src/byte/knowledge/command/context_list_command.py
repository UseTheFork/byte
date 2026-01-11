from argparse import Namespace

from rich.columns import Columns

from byte.cli import ByteArgumentParser, Command
from byte.knowledge import SessionContextService
from byte.support.mixins import UserInteractive


class ContextListCommand(Command, UserInteractive):
    """List all session context items currently stored."""

    @property
    def name(self) -> str:
        return "ctx:ls"

    @property
    def category(self) -> str:
        return "Session Context"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="List all session context items",
        )
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Display all session context keys in a formatted panel.

        Usage: `await command.execute("")`
        """
        console = self.app["console"]

        session_context_service = self.app.make(SessionContextService)
        session_context = session_context_service.get_all_context()

        context_keys = [f"[text]{key}[/text]" for key in session_context.keys()]
        context_panel = console.panel(
            Columns(context_keys, equal=True, expand=True),
            title=f"Session Context Items ({len(session_context)})",
        )

        console.print(context_panel)
