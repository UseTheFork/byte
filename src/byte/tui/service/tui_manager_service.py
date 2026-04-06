from byte import CommandRegistryService, Events
from byte.support import Service
from byte.tui import TuiEvents


class TUIManagerService(Service):
    """ """

    # Manages the Textual TUI entrypoint etc.

    def boot(self) -> None:
        """Initialize the chatbox manager with empty state.

        Usage: Called automatically during service container boot process
        """
        from byte.tui.byte_tui import ByteTUI

        self.tui = ByteTUI(container=self.app)
        self.command_registry = self.app.make(CommandRegistryService)
        self.pending_panel = None

    async def run_async(self):
        await self.tui.run_async()

    async def _create_pending_panel(self):
        self.pending_panel = await self.tui.mount_pending_response_panel()

        # self.pending_panel.rune_spinner.display = "none"
        # self.pending_panel.agent_response_widget.update(event.chunk)
        # current_chatbox.agent_response_widget.update(self.current_chatbox.response)

    async def route_event(self, event: Events.TuiEvent):
        tui_event = event.event

        if isinstance(tui_event, TuiEvents.Notify):
            self.tui.flash(
                tui_event.content,
                style=tui_event.style,
                duration=tui_event.duration,
            )
            return

        if isinstance(tui_event, TuiEvents.CommandExecutionStarted):
            await self._create_pending_panel()
            return

        if isinstance(tui_event, TuiEvents.UpdateAnalytics):
            self.tui.analytics(
                tokens_sent=tui_event.tokens_sent,
                tokens_received=tui_event.tokens_received,
                message_cost=tui_event.message_cost,
                session_cost=tui_event.session_cost,
                memory_percent=tui_event.memory_percent,
            )
            return

        assert self.pending_panel is not None, "TuiEvents.CommandExecutionStarted() must be emitted first."

        if isinstance(tui_event, TuiEvents.AddHeading):
            await self.pending_panel.add_heading(tui_event.heading)
        elif isinstance(tui_event, TuiEvents.ResponseStarted):
            await self.pending_panel.start_markdown_stream()
        elif isinstance(tui_event, TuiEvents.ResponseChunk):
            await self.pending_panel.add_markdown_chunk(tui_event.chunk)
        elif isinstance(tui_event, TuiEvents.ResponseComplete):
            await self.pending_panel.end_markdown_stream()

        self.tui.conversation.scroll_to_latest_message()

        # # TODO: We need a fallback here.

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

        # console = self.app["console"]

        # Get command registry and execute
        command_registry = self.app.make(CommandRegistryService)
        command = command_registry.get_slash_command(command_name)

        if command:
            await command.handle(args)
        else:
            pass
            # TODO: This should flash an error
            # console.print_error(f"Unknown command: /{command_name}")

    async def handle_user_message(self, event: Events.UserInputSubmitted):
        user_input = event.message

        # User Messages are always our primary entrypoint. As a result we always create a pending panel here and mount it empty.
        #

        if user_input.startswith("/"):
            await self._handle_command_input(event.message)
