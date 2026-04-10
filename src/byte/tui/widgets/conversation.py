from __future__ import annotations

from typing import TYPE_CHECKING

from textual import getters, on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widget import Widget

from byte import EventBus
from byte.tui import TuiEvents
from byte.tui.messages import Messages
from byte.tui.schemas import Ask
from byte.tui.widgets.chatbox import Chatbox
from byte.tui.widgets.panels.human_message_panel import HumanMessagePanel
from byte.tui.widgets.panels.pending_panel import PendingPanel
from byte.tui.widgets.prompt.analytics import Analytics
from byte.tui.widgets.prompt.flash import Flash
from byte.tui.widgets.prompt.prompt_panel import PromptPanel
from byte.tui.widgets.ui.loading_indicator import LoadingIndicator

if TYPE_CHECKING:
    from byte.tui import ByteTUI


class Conversation(Widget):
    BINDING_GROUP_TITLE = "Conversation"

    BINDINGS = [
        Binding("ctrl+r", "rename", "Rename", key_display="^r"),
        Binding("shift+down", "scroll_container_down", show=False),
        Binding("shift+up", "scroll_container_up", show=False),
        Binding(
            key="g",
            action="focus_first_message",
            description="First message",
            key_display="g",
            show=False,
        ),
        Binding(
            key="G",
            action="focus_latest_message",
            description="Latest message",
            show=False,
        ),
        Binding(key="f2", action="details", description="Chat info"),
    ]

    app: ByteTUI

    pending_panel: PendingPanel | None = None

    # Used to lock the chat input while the agent is responding.
    allow_input_submit = reactive(True)

    prompt = getters.query_one("#prompt", PromptPanel)
    chat_container = getters.query_one("#chat-container", VerticalScroll)
    loading_indicator = getters.query_one(LoadingIndicator)

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

        self.event_bus = self.app.byte.make(EventBus)

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="chat-container") as vertical_scroll:
            vertical_scroll.can_focus = False
        yield PromptPanel(id="prompt")

    def scroll_to_latest_message(self):
        container = self.chat_container
        container.refresh()
        container.scroll_end(animate=False, force=True)

    # @on(PromptPanel.CursorEscapingTop)
    # async def on_cursor_up_from_prompt(self, event: PromptPanel.CursorEscapingTop) -> None:
    #     self.focus_latest_message()

    @on(Chatbox.CursorEscapingBottom)
    def move_focus_to_prompt(self) -> None:
        self.query_one(PromptPanel).focus()

    def get_latest_chatbox(self) -> Chatbox:
        return self.query(Chatbox).last()

    def focus_latest_message(self) -> None:
        try:
            self.get_latest_chatbox().focus()
        except NoMatches:
            pass

    def action_focus_latest_message(self) -> None:
        self.focus_latest_message()

    def action_focus_first_message(self) -> None:
        try:
            self.query(Chatbox).first().focus()
        except NoMatches:
            pass

    def action_scroll_container_up(self) -> None:
        if self.chat_container:
            self.chat_container.scroll_up()

    def action_scroll_container_down(self) -> None:
        if self.chat_container:
            self.chat_container.scroll_down()

    def action_close(self) -> None:
        self.app.clear_notifications()
        self.app.pop_screen()

    @on(Messages.UserInputSubmitted)
    async def new_user_message(self, event: Messages.UserInputSubmitted) -> None:
        """Handle a new user message."""
        self.allow_input_submit = False

        user_message_chatbox = HumanMessagePanel(event.body)
        await self.chat_container.mount(user_message_chatbox)
        self.scroll_to_latest_message()
        self.emit_user_input_submitted(event)

    @work(thread=True)
    async def emit_user_input_submitted(self, event: Messages.UserInputSubmitted):
        # TODO: should we make this none blocking?
        await self.event_bus.emit(
            TuiEvents.UserInputSubmitted(
                event.body,
            )
        )

    async def mount_pending_response_panel(self):
        if self.pending_panel is None:
            pending_panel = PendingPanel()
            await self.chat_container.mount(pending_panel)

            self.chat_container.refresh(layout=True)
            self.pending_panel = pending_panel

    @on(Messages.CommandExecutionStarted)
    async def command_execution_started(self, event: Messages.CommandExecutionStarted) -> None:
        await self.mount_pending_response_panel()
        self.loading_indicator.show("Thinking")

    @on(Messages.CreatePanel)
    async def create_panel(self, event: Messages.CreatePanel) -> None:
        await self.mount_pending_response_panel()
        await self.pending_panel.mount_panel(event)
        self.scroll_to_latest_message()

    @on(Messages.AddHeading)
    async def add_heading(self, event: Messages.AddHeading) -> None:
        assert self.pending_panel
        await self.pending_panel.add_heading(event.heading)
        self.scroll_to_latest_message()

    @on(Messages.ResponseStarted)
    async def response_started(self, event: Messages.ResponseStarted) -> None:
        assert self.pending_panel
        await self.pending_panel.start_markdown_stream()
        self.scroll_to_latest_message()

    @on(Messages.ResponseChunk)
    async def response_chunk(self, event: Messages.ResponseChunk) -> None:
        assert self.pending_panel
        await self.pending_panel.add_markdown_chunk(event.chunk)
        self.scroll_to_latest_message()

    @on(Messages.ResponseComplete)
    async def response_complete(self, event: Messages.ResponseComplete) -> None:
        assert self.pending_panel
        await self.pending_panel.end_markdown_stream()
        self.scroll_to_latest_message()
        self.pending_panel = None

    @on(Messages.Notify)
    async def flash(self, event: Messages.Notify) -> None:
        """Flash a single-line message to the user.

        Args:
            content: Content to flash.
            style: A semantic style.
            duration: Duration in seconds of the flash, or `None` to use default in settings.
        """
        self.query_one(Flash).flash(event.content, duration=event.duration, style=event.style)

    @on(Messages.UpdateAnalytics)
    async def analytics(self, event: Messages.UpdateAnalytics) -> None:
        """Update analytics display with token usage and cost information.

        Args:
            tokens_sent: Number of tokens sent in the last message.
            tokens_received: Number of tokens received in the last message.
            message_cost: Cost of the last message in dollars.
            session_cost: Total cost of the session in dollars.
            memory_percent: Percentage of memory used (0-100).
        """
        self.query_one(Analytics).update_analytics(
            tokens_sent=event.tokens_sent,
            tokens_received=event.tokens_received,
            message_cost=event.message_cost,
            session_cost=event.session_cost,
            memory_percent=event.memory_percent,
        )

    @on(Messages.UpdateFiles)
    async def update_files(self, event: Messages.UpdateFiles) -> None:
        """Update file counts display with current context statistics.

        Args:
            editable: Number of editable files in context.
            read_only: Number of read-only files in context.
        """
        self.query_one(Analytics).update_files(editable=event.editable, read_only=event.read_only)

    @on(Messages.PromptUser)
    async def handle_prompt_user(self, event: Messages.PromptUser):
        await self.mount_pending_response_panel()
        assert self.pending_panel

        if event.prompt_type == "select":
            ask = Ask(
                question=event.question,
                options=event.options,
                result_future=event.result_future,
            )
            await self.pending_panel.mount_select(ask)
        else:
            ask = Ask(
                question=event.question,
                options=None,
                result_future=event.result_future,
            )
            await self.pending_panel.mount_input(ask)

    @on(Messages.LintStarted)
    async def lint_started(self, event: Messages.LintStarted) -> None:
        """Handle linting operation start."""
        await self.mount_pending_response_panel()
        assert self.pending_panel
        await self.pending_panel.create_linting(event.file_count, event.command_count)
        self.scroll_to_latest_message()

    @on(Messages.LintProgress)
    async def lint_progress(self, event: Messages.LintProgress) -> None:
        """Handle linting progress update."""
        assert self.pending_panel
        await self.pending_panel.update_linting_progress(event.current_file, event.completed, event.total)
        self.scroll_to_latest_message()

    @on(Messages.LintCompleted)
    async def lint_completed(self, event: Messages.LintCompleted) -> None:
        """Handle linting operation completion."""
        assert self.pending_panel
        await self.pending_panel.complete_linting(event.total_files, event.failed_files, event.success)
        self.scroll_to_latest_message()

    @on(Messages.LoadingIndicatorShow)
    async def loading_indicator_show(self, event: Messages.LoadingIndicatorShow) -> None:
        """Show the loading indicator with an optional message."""
        self.loading_indicator.show(event.message)

    @on(Messages.LoadingIndicatorHide)
    async def loading_indicator_hide(self, event: Messages.LoadingIndicatorHide) -> None:
        """Hide the loading indicator."""
        self.loading_indicator.hide()
