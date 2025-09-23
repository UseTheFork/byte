from byte.core.service.mixins import UserInteractive
from byte.domain.cli_input.service.command_registry import Command
from byte.domain.files.service.file_service import FileService


class ListFilesCommand(Command, UserInteractive):
    """XX"""

    @property
    def name(self) -> str:
        return "ls"

    @property
    def description(self) -> str:
        return "XX"

    async def execute(self, args: str) -> None:
        """XX"""
        file_service = await self.make(FileService)
        await file_service.list_in_context_files()

        # AI: The below is here for testing.

        result = await self.prompt_for_confirmation("test", True)
        print(result)
