from byte.domain.cli_input.service.command_registry import Command
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
    def description(self) -> str:
        return "List all files currently in the AI context"

    async def execute(self, args: str) -> None:
        """Execute the list files command by displaying current context files.

        Usage: Called automatically when user types `/ls`
        """
        file_service = await self.make(FileService)
        await file_service.list_in_context_files()
