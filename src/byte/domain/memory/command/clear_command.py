from rich.console import Console

from byte.domain.cli.service.command_registry import Command
from byte.domain.memory.service.memory_service import MemoryService


class ClearCommand(Command):
    """Command to clear conversation history and start a fresh thread.

    Creates a new conversation thread, effectively clearing the current
    conversation context and starting fresh with no prior message history.
    Usage: `/clear` -> starts new conversation thread
    """

    @property
    def name(self) -> str:
        return "clear"

    @property
    def description(self) -> str:
        return "Clear conversation history and start a new thread"

    async def execute(self, args: str) -> None:
        """Execute the clear command to create a new conversation thread.

        Creates a new thread through the memory service, discarding the current
        conversation history and establishing a fresh context for future messages.

        Args:
            args: Unused for this command

        Usage: Called automatically when user types `/clear`
        """

        memory_service = await self.make(MemoryService)
        await memory_service.new_thread()

        console = await self.make(Console)
        # Display success confirmation to user
        console.print("[success]Conversation history cleared[/success]")
