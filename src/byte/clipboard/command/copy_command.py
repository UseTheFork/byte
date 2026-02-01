from argparse import Namespace

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
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Copy code blocks from message history to clipboard",
        )
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Execute the copy command by running the CopyAgent."""
        import pyperclip

        clipboard_service = self.app.make(ClipboardService)
        console = self.app["console"]

        # Get all stored code blocks
        code_blocks = clipboard_service.get_code_blocks()

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
