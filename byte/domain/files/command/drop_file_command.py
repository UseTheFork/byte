from typing import List

from rich.console import Console

from byte.domain.cli_input.service.command_registry import Command
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
    def description(self) -> str:
        return "Remove file from context"

    async def execute(self, args: str) -> None:
        """Remove specified file from active context."""
        console = await self.make(Console)
        if not args:
            console.print("Usage: /drop <file_path>")
            await self.prompt_for_input()
            return

        file_service: FileService = await self.make(FileService)
        if await file_service.remove_file(args):
            console.print(f"[success]Removed {args} from context[/success]")
            await self.prompt_for_input()
            return
        else:
            console.print(f"[error]File {args} not found in context[/error]")
            await self.prompt_for_input()
            return

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
