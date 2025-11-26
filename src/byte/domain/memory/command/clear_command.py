from argparse import Namespace

from rich.panel import Panel

from byte.domain.analytics.service.agent_analytics_service import AgentAnalyticsService
from byte.domain.cli.argparse.base import ByteArgumentParser
from byte.domain.cli.service.command_registry import Command
from byte.domain.cli.service.console_service import ConsoleService
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

        memory_service = await self.make(MemoryService)
        await memory_service.new_thread()

        agent_analytics_service = await self.make(AgentAnalyticsService)
        agent_analytics_service.reset_context()

        console = await self.make(ConsoleService)
        # Display success confirmation to user
        console.print(Panel("[success]Conversation history cleared[/success]"))
