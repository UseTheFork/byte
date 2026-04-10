from byte import CommandRegistryService
from byte.files import FileEvents
from byte.support import Service
from byte.tui import TuiEvents


class TUIManagerService(Service):
    """ """

    # Manages the Textual TUI entrypoint etc.

    def boot(self) -> None:
        """Initialize the chatbox manager with empty state.

        Usage: Called automatically during service container boot process
        """

        self.tui = self.app.tui()
        self.command_registry = self.app.make(CommandRegistryService)
        self.pending_panel = None

    async def run_async(self):
        await self.tui.run_async()

    async def _create_pending_panel(self):
        if self.pending_panel is None:
            self.pending_panel = await self.tui.mount_pending_response_panel()

    async def _handle_command_input(self, user_input: str):
        """Parse and execute slash commands.

        Args:
                user_input: Raw user input starting with /

        Usage: Called internally when user input starts with /
        """
        # Parse command name and args
        parts = user_input[1:].split(" ", 1)  # Remove "/" and split
        command_name = parts[0]
        args = parts[1] if len(parts) > 1 else ""

        self.app["log"].info(user_input)

        # Get command registry and execute
        command_registry = self.app.make(CommandRegistryService)
        command = command_registry.get_slash_command(command_name)

        if command:
            await command.handle(args)
        else:
            pass
            # TODO: This should flash an error
            # console.print_error(f"Unknown command: /{command_name}")

    async def handle_user_message(self, event: TuiEvents.UserInputSubmitted):
        user_input = event.message

        # User Messages are always our primary entrypoint. As a result we always create a pending panel here and mount it empty.
        if user_input.startswith("/"):
            await self._handle_command_input(event.message)

    async def on_file_events_file_stats(self, event: FileEvents.FileStats):
        self.tui.update_files(
            editable=event.editable,
            read_only=event.read_only,
        )
        return
