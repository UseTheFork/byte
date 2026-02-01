from argparse import Namespace
from typing import List

from byte import Command
from byte.cli import ByteArgumentParser, CodeBlockNavigator
from byte.clipboard import ClipboardService


class CopyCommand(Command):
    """Command to copy code blocks from the last AI message to clipboard.

    Extracts all code blocks from the most recent assistant response,
    displays truncated previews, and allows user selection for copying.
    Usage: `/copy` in the CLI
    """

    @property
    def name(self) -> str:
        return "copy"

    @property
    def category(self) -> str:
        return "Clipboard"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Copy code blocks from message history to clipboard",
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
        """Execute the copy command by running the CopyAgent."""
        import pyperclip

        clipboard_service = self.app.make(ClipboardService)
        console = self.app["console"]

        # Get all stored code blocks, optionally filtered by type
        block_type = args.type if args.type else None
        code_blocks = clipboard_service.get_code_blocks(block_type=block_type)

        if not code_blocks:
            console.print_warning("No code blocks found in the session.")
            return

        # Create navigator and let user select
        navigator = CodeBlockNavigator(code_blocks, console=console.console, transient=True)
        selected_block = navigator.navigate()

        if selected_block is not None:
            # Copy to clipboard
            pyperclip.copy(selected_block.content)
            console.print_success(f"Copied {selected_block.language} code block to clipboard!")

    async def get_completions(self, text: str) -> List[str]:
        """Provide completions for the --type argument."""
        if "--type" in text or text.startswith("-"):
            return ["--type message", "--type block"]
        return []
