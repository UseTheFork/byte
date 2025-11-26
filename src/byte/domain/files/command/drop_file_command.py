from argparse import Namespace
from typing import List

from byte.domain.cli.argparse.base import ByteArgumentParser
from byte.domain.cli.service.command_registry import Command
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.files.service.file_service import FileService


class DropFileCommand(Command):
    """Command to remove files from AI context.

    Enables users to clean up context by removing files that are no
    longer relevant, reducing noise and improving AI focus on current task.
    Usage: `/drop old_file.py` -> removes file from AI awareness
    """

    @property
    def name(self) -> str:
        return "drop"

    @property
    def category(self) -> str:
        return "Files"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Remove file from context",
        )
        parser.add_argument("file_path", help="Path to file")
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Remove specified file from active context."""
        console = await self.make(ConsoleService)

        file_path = args.file_path

        file_service: FileService = await self.make(FileService)
        if await file_service.remove_file(file_path):
            console.print(f"[success]Removed {file_path} from context[/success]")
            return
        else:
            console.print(f"[error]File {file_path} not found in context[/error]")
            return

    async def get_completions(self, text: str) -> List[str]:
        """Provide completions showing files currently in the context.

        Returns relative paths of files in context that match the input pattern,
        allowing users to easily select which files to drop.
        Usage: Tab completion shows only files currently in AI context
        """
        try:
            file_service = await self.make(FileService)

            # Get all files currently in context
            context_files = file_service.list_files()

            # Extract relative paths
            all_context_paths = [f.relative_path for f in context_files]

            # Filter by text pattern if provided
            if text:
                text_lower = text.lower()
                return [path for path in all_context_paths if text_lower in path.lower()]

            return all_context_paths
        except Exception:
            return []
