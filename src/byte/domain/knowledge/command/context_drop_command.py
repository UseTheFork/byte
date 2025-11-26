from argparse import Namespace
from typing import List

from byte.domain.cli.argparse.base import ByteArgumentParser
from byte.domain.cli.service.command_registry import Command
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.knowledge.service.session_context_service import SessionContextService


class ContextDropCommand(Command):
    """Command to remove items from session context.

    Enables users to clean up session context by removing items that are no
    longer relevant, reducing noise and improving AI focus on current task.
    Usage: `/context:drop item_key` -> removes item from session context
    """

    @property
    def name(self) -> str:
        return "ctx:drop"

    @property
    def category(self) -> str:
        return "Session Context"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Remove items from session context to clean up and reduce noise, improving AI focus on current task",
        )
        parser.add_argument("file_path", help="Path to file")
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Remove specified item from session context."""
        console = await self.make(ConsoleService)

        args_file_path = args.file_path

        session_context_service = await self.make(SessionContextService)
        context_items = session_context_service.get_all_context()

        if args_file_path in context_items:
            session_context_service.remove_context(args_file_path)
            console.print(f"[success]Removed {args_file_path} from session context[/success]")
            return
        else:
            console.print(f"[error]Context item {args_file_path} not found[/error]")
            return

    async def get_completions(self, text: str) -> List[str]:
        """Provide intelligent context key completions.

        Suggests existing context keys that match the input pattern.
        """
        try:
            session_context_service = await self.make(SessionContextService)
            context_items = session_context_service.get_all_context()

            # Filter keys that start with the input text
            matches = [key for key in context_items.keys() if key.startswith(text)]
            return matches
        except Exception:
            return []
