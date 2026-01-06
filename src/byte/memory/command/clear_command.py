from argparse import Namespace

from rich.panel import Panel

from byte import Console
from byte.analytics import AgentAnalyticsService
from byte.cli import ByteArgumentParser, Command
from byte.memory import MemoryService


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
    def category(self) -> str:
        return "Memory"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Clear conversation history and start a new thread",
        )
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Execute the clear command to create a new conversation thread.

        Creates a new thread through the memory service, discarding the current
        conversation history and establishing a fresh context for future messages.
        """

        memory_service = self.make(MemoryService)
        await memory_service.new_thread()

        agent_analytics_service = self.make(AgentAnalyticsService)
        agent_analytics_service.reset_context()

        console = self.make(Console)
        # Display success confirmation to user
        console.print(Panel("[success]Conversation history cleared[/success]"))
