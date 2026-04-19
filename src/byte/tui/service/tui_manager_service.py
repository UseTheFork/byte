import threading
import uuid

from byte import CommandRegistryService
from byte.support import Service
from byte.tui import Messages, PromptHistoryService, TuiEvents


class TUIManagerService(Service):
    """ """

    # Manages the Textual TUI entrypoint as well as command handeling.

    def boot(self) -> None:
        """Initialize the chatbox manager with empty state.

        Usage: Called automatically during service container boot process
        """

        self.tui = self.app.tui()
        self.command_registry = self.app.make(CommandRegistryService)
        self.thread_local = threading.local()

    async def run_async(self):
        await self.tui.run_async()

    async def _handle_command_input(self, user_input: str):
        """Parse and execute slash commands.

        Args:
                user_input: Raw user input starting with /

        Usage: Called internally when user input starts with /
        """
        self.app["log"].info("_handle_command_input")

        history_service = self.app.make(PromptHistoryService)
        history_service.append_string(user_input)

        # Parse command name and args
        parts = user_input[1:].split(" ", 1)  # Remove "/" and split
        command_name = parts[0]
        args = parts[1] if len(parts) > 1 else ""

        # Get command registry and execute
        command_registry = self.app.make(CommandRegistryService)
        command = command_registry.get_slash_command(command_name)

        await self.emit_tui(Messages.CommandExecutionStarted())

        if command:
            await command.handle(args)
        else:
            pass
            # TODO: This should flash an error
            # console.print_error(f"Unknown command: /{command_name}")

        await self.emit_tui(Messages.CommandExecutionCompleted())

    async def handle_user_message(self, event: TuiEvents.UserInputSubmitted):
        user_input = event.message

        panel_id = f"panel_{str(uuid.uuid4()).replace('-', '_')}"
        self.thread_local.panel_id = panel_id

        self.tui.conversation.post_message(Messages.CommandExecutionStarted(panel_id=self.thread_local.panel_id))
        # User Messages are always our primary entrypoint. As a result we always create a pending panel here and mount it empty.
        if user_input.startswith("/"):
            await self._handle_command_input(event.message)

        self.tui.conversation.post_message(Messages.CommandExecutionCompleted(panel_id=self.thread_local.panel_id))

    def get_panel_id(self) -> str:
        """Get the current panel ID for this thread.

        Returns:
            The UUID panel_id for the current thread

        Usage: `panel_id = self.get_panel_id()`
        """
        return self.thread_local.panel_id
