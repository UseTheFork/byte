from argparse import Namespace

from byte import Command
from byte.analytics import AgentAnalyticsService
from byte.cli import ByteArgumentParser, InputCancelledError
from byte.files import FileService
from byte.knowledge import SessionContextService
from byte.memory import MemoryService


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
        memory_service = self.app.make(MemoryService)
        await memory_service.new_thread()

        file_service = self.app.make(FileService)
        await file_service.clear_context()

        agent_analytics_service = self.app.make(AgentAnalyticsService)
        agent_analytics_service.reset_context()

        console = self.app["console"]

        # Check if user wants to drop SessionContext as well
        session_context_service = self.app.make(SessionContextService)
        context_items = session_context_service.get_all_context()

        if context_items:
            try:
                drop_session_context = console.confirm(
                    "Also clear session context (conventions, documentation, etc.)?",
                    default=False,
                )

                if drop_session_context:
                    session_context_service.clear_context()
                    console.print(
                        console.panel(
                            "[success]Conversation, file context, and session context completely reset[/success]"
                        )
                    )
                else:
                    console.print(console.panel("[success]Conversation and file context completely reset[/success]"))

            except (KeyboardInterrupt, InputCancelledError):
                console.print(console.panel("[success]Conversation and file context completely reset[/success]"))
        else:
            # Display success confirmation to user
            console.print(console.panel("[success]Conversation and file context completely reset[/success]"))
