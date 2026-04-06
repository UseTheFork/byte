from byte import CommandRegistryService
from byte.files import FileEvents
from byte.support import Service
from byte.tui import TuiComponentEvents, TuiEvents
from byte.tui.schemas import Ask


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
        self.tui.loading_indicator.show("Thinking")

    async def route_event(self, event: TuiEvents.ComponentEvent):
        tui_event = event.event

        if isinstance(tui_event, TuiComponentEvents.Notify):
            self.tui.flash(
                tui_event.content,
                style=tui_event.style,
                duration=tui_event.duration,
            )
            return

        if isinstance(tui_event, TuiComponentEvents.CommandExecutionStarted):
            await self._create_pending_panel()
            return

        if isinstance(tui_event, TuiComponentEvents.UpdateAnalytics):
            self.tui.analytics(
                tokens_sent=tui_event.tokens_sent,
                tokens_received=tui_event.tokens_received,
                message_cost=tui_event.message_cost,
                session_cost=tui_event.session_cost,
                memory_percent=tui_event.memory_percent,
            )
            return

        assert self.pending_panel is not None, "TuiComponentEvents.CommandExecutionStarted() must be emitted first."

        if isinstance(tui_event, TuiComponentEvents.AddHeading):
            await self.pending_panel.add_heading(tui_event.heading)
        elif isinstance(tui_event, TuiComponentEvents.ResponseStarted):
            await self.pending_panel.start_markdown_stream()
        elif isinstance(tui_event, TuiComponentEvents.ResponseChunk):
            await self.pending_panel.add_markdown_chunk(tui_event.chunk)
            self.tui.loading_indicator.hide()
        elif isinstance(tui_event, TuiComponentEvents.ResponseComplete):
            await self.pending_panel.end_markdown_stream()
            self.tui.loading_indicator.hide()

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

    async def handle_ask_question(self, event: TuiEvents.AskQuestion):
        question_widget = self.tui.prompt.question

        ask = Ask(
            question=event.question,
            options=event.options,
            result_future=event.result_future,
        )
        question_widget.update(ask)

        # Switch prompt to ask mode
        self.tui.prompt.prompt_input.visible = False
        self.tui.prompt.question.visible = True

        self.tui.prompt.add_class("-mode-ask")
        question_widget.focus()
