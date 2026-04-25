from typing import TYPE_CHECKING

from textual import getters, on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widget import Widget

from byte import EventBus
from byte.support import Str
from byte.tui import Status, TuiEvents
from byte.tui.messages import Messages
from byte.tui.schemas import Ask
from byte.tui.widgets.panels.response_panel import ResponsePanel
from byte.tui.widgets.prompt.analytics import Analytics
from byte.tui.widgets.prompt.prompt_input import PromptTextArea
from byte.tui.widgets.prompt.prompt_panel import PromptPanel
from byte.tui.widgets.prompt.status_bar import StatusBar
from byte.tui.widgets.ui.selectable_markdown import SelectableMarkdown

if TYPE_CHECKING:
    from byte.tui import ByteTUI


class Conversation(Widget):
    BINDING_GROUP_TITLE = "Conversation"

    BINDINGS = [
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
    ]

    app: ByteTUI

    # Used to lock the chat input while the agent is responding.
    allow_input_submit = reactive(True)

    prompt = getters.query_one("#prompt", PromptPanel)
    prompt_text_area = getters.query_one(PromptTextArea)
    status_bar = getters.query_one(StatusBar)
    chat_container = getters.query_one("#chat-container", VerticalScroll)

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
        yield PromptPanel(id="prompt").data_bind(allow_input_submit=Conversation.allow_input_submit)

    def scroll_to_latest_message(self):
        container = self.chat_container
        container.refresh()
        container.scroll_end(animate=False, force=True)

    # @on(PromptPanel.CursorEscapingTop)
    # async def on_cursor_up_from_prompt(self, event: PromptPanel.CursorEscapingTop) -> None:
    #     self.focus_latest_message()

    @on(SelectableMarkdown.CursorEscapingBottom)
    def move_focus_to_prompt(self) -> None:
        self.query_one(PromptTextArea).focus()

    def get_latest_chatbox(self) -> SelectableMarkdown:
        return self.query(SelectableMarkdown).last()

    def focus_latest_message(self) -> None:
        try:
            self.get_latest_chatbox().focus()
        except NoMatches:
            pass

    def action_focus_latest_message(self) -> None:
        self.focus_latest_message()

    def action_focus_first_message(self) -> None:
        try:
            self.query(SelectableMarkdown).first().focus()
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
        if self.allow_input_submit is False:
            return

        if not event.body or not event.body.strip():
            return

        self.allow_input_submit = False
        self.emit_user_input_submitted(event)

    @work(thread=True)
    async def emit_user_input_submitted(self, event: Messages.UserInputSubmitted):
        # TODO: should we make this none blocking?
        await self.event_bus.emit(
            TuiEvents.UserInputSubmitted(
                event.body,
                interrupted=event.interrupted,
            )
        )

    async def get_or_create_response_panel(self, panel_id: str | None) -> ResponsePanel:
        if panel_id is None:
            raise ValueError("panel_id cannot be None")

        try:
            pending_panel = self.query_one(f"#{panel_id}", ResponsePanel)
            return pending_panel
        except NoMatches:
            pending_panel = ResponsePanel(id=panel_id)
            await self.chat_container.mount(pending_panel)
            self.chat_container.refresh(layout=True)
            return pending_panel

    @on(Messages.CommandExecutionStarted)
    async def command_execution_started(self, event: Messages.CommandExecutionStarted) -> None:
        await self.get_or_create_response_panel(event.panel_id)

    @on(Messages.CommandExecutionCompleted)
    async def command_execution_completed(self, event: Messages.CommandExecutionCompleted) -> None:
        self.post_message(Messages.Status())
        self.move_focus_to_prompt()
        self.allow_input_submit = True

    @on(Messages.CreatePanel)
    async def create_panel(self, event: Messages.CreatePanel) -> None:
        response_panel = await self.get_or_create_response_panel(event.panel_id)
        await response_panel.mount_panel(event)
        self.scroll_to_latest_message()

    @on(Messages.AddUserInput)
    async def add_user_message(self, event: Messages.AddUserInput) -> None:
        response_panel = await self.get_or_create_response_panel(event.panel_id)
        await response_panel.add_user_message(event)
        self.scroll_to_latest_message()

    @on(Messages.CreateHeading)
    async def add_heading(self, event: Messages.CreateHeading) -> None:
        response_panel = await self.get_or_create_response_panel(event.panel_id)
        await response_panel.add_heading(event)
        self.scroll_to_latest_message()

    @on(Messages.Response)
    async def handle_response(self, event: Messages.Response) -> None:
        response_panel = await self.get_or_create_response_panel(event.panel_id)

        # Control the indicator display state.
        if isinstance(event.with_indicator, bool):
            self.post_message(Messages.Status(state="loading", message="Thinking..."))
        elif isinstance(event.with_indicator, str):
            self.post_message(Messages.Status(state="loading", message=event.with_indicator))

        if event.status is Status.PENDING:
            heading = Str.snake_to_title(str(event.chunk)).replace(" Node", "").strip()
            await response_panel.start_markdown_stream(heading)
        elif event.status is Status.RUNNING:
            await response_panel.add_markdown_chunk(str(event.chunk))
        elif event.status is Status.SUCCESS:
            await response_panel.end_markdown_stream()
            self.post_message(Messages.Status())

        self.scroll_to_latest_message()

    @on(Messages.ToolResponse)
    async def handle_tool_response(self, event: Messages.ToolResponse) -> None:
        response_panel = await self.get_or_create_response_panel(event.panel_id)

        if event.status is Status.PENDING:
            self.post_message(Messages.Status(state="loading", message="Using Tool..."))
            await response_panel.start_tool_stream(
                tool_name=str(event.tool_name),
                tool_id=str(event.tool_id),
            )
        elif event.status is Status.RUNNING:
            await response_panel.add_tool_chunk(event.tool_id, str(event.chunk))
        elif event.status is Status.SUCCESS:
            await response_panel.end_tool_stream(event.tool_id)
            self.post_message(Messages.Status())

        self.scroll_to_latest_message()

    @on(Messages.PromptUser)
    async def handle_prompt_user(self, event: Messages.PromptUser):
        response_panel = await self.get_or_create_response_panel(event.panel_id)

        if event.prompt_type == "select":
            ask = Ask(
                question=event.question,
                options=event.options,
                result_future=event.result_future,
            )
            await response_panel.mount_select(ask)
        else:
            ask = Ask(
                question=event.question,
                options=None,
                result_future=event.result_future,
            )
            await response_panel.mount_input(ask)

        self.scroll_to_latest_message()

    @on(Messages.Lint)
    async def handle_lint(self, event: Messages.Lint) -> None:
        """Handle linting operation with status-based dispatch."""
        response_panel = await self.get_or_create_response_panel(event.panel_id)

        if event.status is Status.PENDING:
            await response_panel.create_linting(event)
        elif event.status is Status.RUNNING:
            await response_panel.update_linting_progress(str(event.current_file), event.completed, event.total)
        elif event.status is Status.SUCCESS:
            await response_panel.complete_linting(event.total_files, event.failed_files, event.success)

        self.scroll_to_latest_message()

    @on(Messages.LintResults)
    async def lint_results(self, event: Messages.LintResults) -> None:
        """Handle lint results display."""
        response_panel = await self.get_or_create_response_panel(event.panel_id)
        if response_panel.current_linting is not None:
            response_panel.current_linting.display_results(event.content)
        self.scroll_to_latest_message()

    @on(Messages.Status)
    async def update_status(self, event: Messages.Status) -> None:
        """Show the loading indicator with an optional message."""
        if event.state == "loading":
            self.status_bar.show_loading()
        else:
            self.status_bar.show_status(event.message if event.message is not None else "", state=event.state)

    @on(Messages.ToolCall)
    async def tool_call(self, event: Messages.ToolCall) -> None:
        """Handle tool call display."""
        response_panel = await self.get_or_create_response_panel(event.panel_id)
        await response_panel.mount_toolcall(event.name, event.args)
        self.scroll_to_latest_message()

    @on(Messages.Notify)
    async def flash(self, event: Messages.Notify) -> None:
        """Flash a single-line message to the user.

        Args:
            content: Content to flash.
            style: A semantic style.
            duration: Duration in seconds of the flash, or `None` to use default in settings.
        """
        self.notify(
            str(event.content),
            # title="Clipboard error",
            severity=event.style,
            timeout=event.duration,
        )

    @on(Messages.UpdateContext)
    async def update_context(self, event: Messages.UpdateContext) -> None:
        """Update context count display with current context statistics.

        Args:
            event: UpdateContext message containing context_count information.
        """
        self.query_one(Analytics).update_context(event)

    @on(Messages.UpdateAnalytics)
    async def analytics(self, event: Messages.UpdateAnalytics) -> None:
        """Update analytics display with token usage and cost information.

        Args:
            event: UpdateAnalytics message containing token usage and cost information.
        """
        self.query_one(Analytics).update_analytics(event)

    @on(Messages.UpdateFiles)
    async def update_files(self, event: Messages.UpdateFiles) -> None:
        """Update file counts display with current context statistics.

        Args:
            event: UpdateFiles message containing editable and read_only file counts.
        """
        self.query_one(Analytics).update_files(event)

    @on(Messages.Clear)
    async def clear_conversation(self, event: Messages.Clear) -> None:
        try:
            for child in self.chat_container.query(ResponsePanel).results():
                await child.remove()
        except Exception:
            pass
