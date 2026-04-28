from argparse import ArgumentParser, Namespace
from typing import List

from byte import Command
from byte.files import FileMode, FileService
from byte.tui import Messages


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
        """Add specified file to context with read-only permissions."""

        self.emit_tui(Messages.CommandExecutionStarted())
        self.emit_tui(Messages.AddUserInput(raw_args, command=self.name))

        file_path = args.file_path

        file_service = self.app.make(FileService)
        result = await file_service.add_file(file_path, FileMode.READ_ONLY)

        if not result:
            await self.notify_error(
                f"Failed to add {file_path} (file not found, not readable, or is already in context)"
            )
        else:
            await self.notify_success(f"Added {file_path} to context")
            await file_service.notify_file_stats()

        self.emit_tui(Messages.CommandExecutionCompleted())

    async def get_completions(self, text: str) -> List[str]:
        """Provide intelligent file path completions from project discovery.

        Uses the same completion logic as AddFileCommand for consistency,
        suggesting project files that match the input pattern.
        """
        try:
            file_service = self.app.make(FileService)

            matches = await file_service.find_project_files(text)
            return [f for f in matches if not await file_service.is_file_in_context(f)]
        except Exception:
            return []
