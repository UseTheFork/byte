from argparse import Namespace

from byte import ByteArgumentParser, Command
from byte.analytics import AgentAnalyticsService
from byte.files import FileService
from byte.knowledge import SessionContextService
from byte.memory import MemoryService
from byte.tui import InputCancelledError, Messages


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

        self.emit_tui(Messages.CommandExecutionStarted())
        self.emit_tui(Messages.AddUserInput(raw_args, command=self.name))

        memory_service = self.app.make(MemoryService)
        await memory_service.new_thread()

        file_service = self.app.make(FileService)
        await file_service.clear_context()

        agent_analytics_service = self.app.make(AgentAnalyticsService)
        agent_analytics_service.reset_context()

        # Check if user wants to drop SessionContext as well
        session_context_service = self.app.make(SessionContextService)
        context_items = session_context_service.get_all_context()

        if context_items:
            try:
                # Emit a confirmation request to TUI
                drop_session_context = await self.prompt_for_confirmation(
                    "Also clear session context (conventions, documentation, etc.)?"
                )

                if drop_session_context:
                    session_context_service.clear_context()
                    await self.notify_success("Conversation, file context, and session context completely reset")
                else:
                    await self.notify_success("Conversation and file context completely reset")

            except KeyboardInterrupt, InputCancelledError:
                await self.notify_success("Conversation and file context completely reset")
        else:
            # Notify success
            await self.notify_success("Conversation and file context completely reset")

        self.emit_tui(Messages.CommandExecutionCompleted())
