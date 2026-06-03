from argparse import Namespace

from rich.columns import Columns

from byte import ByteArgumentParser, Command
from byte.files import FileService


class ListFilesCommand(Command):
    """Command to list all files currently in the AI context.

    Displays both editable and read-only files that are available to the AI,
    organized by access mode with visual indicators for easy identification.
    Usage: `/ls` -> shows all files in current AI context
    """

    @property
    def name(self) -> str:
        return "ls"

    @property
    def category(self) -> str:
        return "Files"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="List all files currently in the AI context",
        )
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Execute the list files command by displaying current context files.

        Usage: Called automatically when user types `/ls`
        """
        console = self.app["console"]
        file_service = self.app.make(FileService)

        # Get all files in context
        files = file_service.list_files()

        # Check if context is empty
        if not files:
            console.print("[info]No files in context[/info]")
            return

        # Display all files
        file_paths = [f"[text]{f.relative_path}[/text]" for f in files]
        panel = console.panel(
            Columns(file_paths, equal=True, expand=True),
            title=f"Files in Context ({len(files)})",
        )
        console.print(panel)
