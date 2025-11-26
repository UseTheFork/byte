from argparse import Namespace

from rich.columns import Columns

from byte.domain.cli.argparse.base import ByteArgumentParser
from byte.domain.cli.service.command_registry import Command
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.files.models import FileMode
from byte.domain.files.service.file_service import FileService


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
        console = await self.make(ConsoleService)
        file_service = await self.make(FileService)

        # Get files by mode
        read_only_files = file_service.list_files(FileMode.READ_ONLY)
        editable_files = file_service.list_files(FileMode.EDITABLE)

        # Check if context is empty
        if not read_only_files and not editable_files:
            console.print("[info]No files in context[/info]")
            return

        # Create panels for each file mode
        panels_to_show = []

        if read_only_files:
            file_paths = [f"[text]{f.relative_path}[/text]" for f in read_only_files]
            read_only_panel = console.panel(
                Columns(file_paths, equal=True, expand=True),
                title=f"Read-Only Files ({len(read_only_files)})",
            )
            panels_to_show.append(read_only_panel)

        if editable_files:
            file_paths = [f"[text]{f.relative_path}[/text]" for f in editable_files]
            editable_panel = console.panel(
                Columns(file_paths, equal=True, expand=True),
                title=f"Editable Files ({len(editable_files)})",
            )
            panels_to_show.append(editable_panel)

        # Display panels in columns layout
        if panels_to_show:
            columns_panel = Columns(panels_to_show, equal=True, expand=True)
            console.print(columns_panel)
