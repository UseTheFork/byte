from argparse import Namespace

from rich.columns import Columns

from byte.core.mixins.user_interactive import UserInteractive
from byte.domain.cli.argparse.base import ByteArgumentParser
from byte.domain.cli.service.command_registry import Command
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.knowledge.service.session_context_service import SessionContextService


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
        console = await self.make(ConsoleService)

        session_context_service = await self.make(SessionContextService)
        session_context = session_context_service.get_all_context()

        context_keys = [f"[text]{key}[/text]" for key in session_context.keys()]
        context_panel = console.panel(
            Columns(context_keys, equal=True, expand=True),
            title=f"Session Context Items ({len(session_context)})",
        )

        console.print(context_panel)
