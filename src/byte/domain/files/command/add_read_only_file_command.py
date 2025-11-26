from argparse import ArgumentParser, Namespace
from typing import List

from byte.domain.cli.service.command_registry import Command
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.files.models import FileMode
from byte.domain.files.service.file_service import FileService


class ReadOnlyCommand(Command):
    """Command to add files to AI context as read-only references.

    Allows AI to reference file content for context without permission
    to modify, useful for configuration files, documentation, or examples.
    Usage: `/read-only config.json` -> file available for reference only
    """

    @property
    def name(self) -> str:
        return "read-only"

    @property
    def category(self) -> str:
        return "Files"

    @property
    def parser(self) -> ArgumentParser:
        parser = ArgumentParser(prog=self.name, description="Add file to context as read-only", add_help=False)
        parser.add_argument("file_path", help="Path to file")
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Add specified file to context with editable permissions."""
        console = await self.make(ConsoleService)

        file_path = args.file_path

        file_service = await self.make(FileService)
        result = await file_service.add_file(file_path, FileMode.READ_ONLY)

        if not result:
            console.print(
                f"[error]Failed to add {file_path} (file not found, not readable, or is already in context)[/error]"
            )

    async def get_completions(self, text: str) -> List[str]:
        """Provide intelligent file path completions from project discovery.

        Uses the same completion logic as AddFileCommand for consistency,
        suggesting project files that match the input pattern.
        """
        try:
            file_service = await self.make(FileService)

            matches = await file_service.find_project_files(text)
            return [f for f in matches if not await file_service.is_file_in_context(f)]
        except Exception:
            return []
