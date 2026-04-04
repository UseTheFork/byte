from argparse import Namespace
from typing import List

from byte import ByteArgumentParser, Command
from byte.cli import InputCancelledError
from byte.knowledge import SessionContextService


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
        parser.add_argument(
            "file_path", nargs="?", help="Path to file (optional - if not provided, shows multiselect menu)"
        )
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Remove specified item from session context."""
        console = self.app["console"]
        session_context_service = self.app.make(SessionContextService)
        context_items = session_context_service.get_all_context()

        if not context_items:
            console.print_warning("No context items to remove")
            return

        args_file_path = args.file_path

        # If file_path is provided, remove that specific item
        if args_file_path:
            if args_file_path in context_items:
                session_context_service.remove_context(args_file_path)
                console.print(f"[success]Removed {args_file_path} from session context[/success]")
                return
            else:
                console.print(f"[error]Context item {args_file_path} not found[/error]")
                return

        # If no file_path provided, show multiselect menu
        context_keys = list(context_items.keys())

        try:
            selected_items = console.multiselect(
                *context_keys,
                title="Select context items to drop",
            )

            if not selected_items:
                console.print_info("No items selected")
                return

            # Remove all selected items
            for item in selected_items:
                session_context_service.remove_context(item)

            if len(selected_items) == 1:
                console.print_success(f"Removed {selected_items[0]} from session context")
            else:
                console.print_success(f"Removed {len(selected_items)} items from session context")

        except (KeyboardInterrupt, InputCancelledError):
            console.print_info("Operation cancelled")
            return

    async def get_completions(self, text: str) -> List[str]:
        """Provide intelligent context key completions.

        Suggests existing context keys that match the input pattern.
        """
        try:
            session_context_service = self.app.make(SessionContextService)
            context_items = session_context_service.get_all_context()

            # Filter keys that start with the input text
            matches = [key for key in context_items.keys() if key.startswith(text)]
            return matches
        except Exception:
            return []
