from argparse import Namespace

from byte import ByteArgumentParser, Command
from byte.analytics import AgentAnalyticsService
from byte.memory import MemoryService
from byte.tui import Messages


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

        self.emit_tui(Messages.CommandExecutionStarted())
        self.emit_tui(Messages.AddUserInput(raw_args, command=self.name))

        memory_service = self.app.make(MemoryService)
        await memory_service.new_thread()

        agent_analytics_service = self.app.make(AgentAnalyticsService)
        agent_analytics_service.reset_context()

        await self.notify_success("Conversation history cleared")
        self.emit_tui(Messages.CommandExecutionCompleted())
