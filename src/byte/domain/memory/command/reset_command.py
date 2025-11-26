from argparse import Namespace

from byte.domain.analytics.service.agent_analytics_service import AgentAnalyticsService
from byte.domain.cli.argparse.base import ByteArgumentParser
from byte.domain.cli.service.command_registry import Command
from byte.domain.cli.service.console_service import ConsoleService
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
    def category(self) -> str:
        return "Memory"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Reset conversation history and clear file context completely",
        )
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Execute the reset command to create a new thread and clear file context.

        Creates a new thread through the memory service and clears all files from
        the file service context, providing a complete reset of the conversation state.
        """
        memory_service = await self.make(MemoryService)
        await memory_service.new_thread()

        file_service = await self.make(FileService)
        await file_service.clear_context()

        agent_analytics_service = await self.make(AgentAnalyticsService)
        agent_analytics_service.reset_context()

        console = await self.make(ConsoleService)

        # Display success confirmation to user
        console.print(console.panel("[success]Conversation and file context completely reset[/success]"))
