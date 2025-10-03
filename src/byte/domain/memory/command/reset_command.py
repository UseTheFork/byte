from rich.console import Console

from byte.domain.cli.rich.panel import Panel
from byte.domain.cli.service.command_registry import Command
from byte.domain.files.service.file_service import FileService
from byte.domain.memory.service.memory_service import MemoryService


class ResetCommand(Command):
    """Command to reset conversation history and file context completely.

    Creates a new conversation thread and clears all files from the current context,
    providing a complete fresh start with no prior message history or file references.
    Usage: `/reset` -> starts new conversation thread and clears file context
    """

    @property
    def name(self) -> str:
        return "reset"

    @property
    def description(self) -> str:
        return "Reset conversation history and clear file context completely"

    async def execute(self, args: str) -> None:
        """Execute the reset command to create a new thread and clear file context.

        Creates a new thread through the memory service and clears all files from
        the file service context, providing a complete reset of the conversation state.

        Args:
            args: Unused for this command

        Usage: Called automatically when user types `/reset`
        """
        memory_service = await self.make(MemoryService)
        await memory_service.new_thread()

        file_service = await self.make(FileService)
        await file_service.clear_context()

        console = await self.make(Console)

        # Display success confirmation to user
        console.print(
            Panel("[success]Conversation and file context completely reset[/success]")
        )
