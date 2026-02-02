from argparse import Namespace
from typing import List

from byte import Command
from byte.cli import ByteArgumentParser
from byte.clipboard import ClipboardService


class CopyDropCommand(Command):
    """Command to clear code blocks from the clipboard session.

    Removes stored code blocks, optionally filtered by type (message or block).
    Usage: `/copy:drop` in the CLI
    """

    @property
    def name(self) -> str:
        return "copy:drop"

    @property
    def category(self) -> str:
        return "Clipboard"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Clear code blocks from the clipboard session",
        )
        parser.add_argument(
            "--type",
            type=str,
            choices=["message", "block"],
            default=None,
            help="Filter code blocks by type (message or block)",
        )
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Execute the copy:drop command by clearing stored code blocks."""
        clipboard_service = self.app.make(ClipboardService)
        console = self.app["console"]

        # Get block type filter if specified
        block_type = args.type if args.type else None

        # Clear code blocks
        clipboard_service.clear_code_blocks(block_type=block_type)

        if block_type:
            console.print_success(f"Cleared all {block_type} code blocks from the session.")
        else:
            console.print_success("Cleared all code blocks from the session.")

    async def get_completions(self, text: str) -> List[str]:
        """Provide completions for the --type argument."""
        if "--type" in text or text.startswith("-"):
            return ["--type message", "--type block"]
        return []
