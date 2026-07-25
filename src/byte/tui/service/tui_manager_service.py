import threading
import uuid

from byte import CommandRegistryService
from byte.support import Service
from byte.tui import Messages, PromptHistoryService, TuiEvents


class TUIManagerService(Service):
    """Manage the Textual TUI entrypoint and command handling."""

    def boot(self) -> None:
        """Initialize the chatbox manager with empty state."""

        self.tui = self.app.tui()
        self.command_registry = self.app.make(CommandRegistryService)
        self.thread_local = threading.local()

    async def run_async(self) -> None:
        """Run the TUI asynchronously."""
        await self.tui.run_async()

    async def _handle_command_input(self, user_input: str):
        """Parse and execute slash commands."""

        # Only append messages the user sends not AI comment messages.
        if not self.is_interrupted():
            history_service = self.app.make(PromptHistoryService)
            history_service.append_string(user_input)

        # Parse command name and args
        parts = user_input[1:].split(" ", 1)  # Remove "/" and split
        command_name = parts[0]
        args = parts[1] if len(parts) > 1 else ""

        # Get command registry and execute
        command_registry = self.app.make(CommandRegistryService)
        command = command_registry.get_slash_command(command_name)

        self.emit_tui(Messages.CommandExecutionStarted())

        if command:
            await command.handle(args)
        else:
            self.emit_tui(Messages.Notify(content=f"Unknown command: /{command_name}", style="error"))

        self.emit_tui(Messages.CommandExecutionCompleted())

    async def handle_user_message(self, event: TuiEvents.UserInputSubmitted) -> None:
        """Handle a user message submission event."""
        user_input = event.message

        panel_id = f"panel_{str(uuid.uuid4()).replace('-', '_')}"
        self.thread_local.panel_id = panel_id

        self.thread_local.is_interrupted = event.interrupted

        self.tui.conversation.post_message(Messages.CommandExecutionStarted(panel_id=self.thread_local.panel_id))
        # User Messages are always our primary entrypoint. As a result we always create a pending panel here and mount it empty.
        if user_input.startswith("/"):
            await self._handle_command_input(event.message)
        else:
            # Assume this is a coder command so prepend that
            await self._handle_command_input(f"/coder {event.message}")

        self.tui.conversation.post_message(Messages.CommandExecutionCompleted(panel_id=self.thread_local.panel_id))

    def get_panel_id(self) -> str:
        """Get the current panel ID for this thread."""
        return self.thread_local.panel_id

    def is_interrupted(self) -> bool:
        """Check if the current thread is interrupted."""
        return self.thread_local.is_interrupted

    def exit(self) -> None:
        """Exit the Byte application gracefully."""
        self.tui.exit()
