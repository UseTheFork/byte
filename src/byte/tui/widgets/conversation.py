from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.content import Content
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widget import Widget

from byte.tui import Messages
from byte.tui.widgets.chatbox import Chatbox
from byte.tui.widgets.flash import Flash
from byte.tui.widgets.prompt import Prompt

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

    # Used to lock the chat input while the agent is responding.
    allow_input_submit = reactive(True)

    def __init__(
        self,
        # chat_data: ChatData,
    ) -> None:
        super().__init__()
        self.chat_data = []
        self.byte_app = self.app.byte

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="chat-container") as vertical_scroll:
            vertical_scroll.can_focus = False
        yield Prompt(id="prompt")

    @property
    def chat_container(self) -> VerticalScroll:
        return self.query_one("#chat-container", VerticalScroll)

    @on(Messages.Flash)
    def on_flash(self, event: Messages.Flash) -> None:
        event.stop()
        self.flash(event.content, duration=event.duration, style=event.style)

    def flash(
        self,
        content: str | Content,
        *,
        duration: float | None = None,
        style: Literal["default", "warning", "error", "success"] = "default",
    ) -> None:
        """Flash a single-line message to the user.

        Args:
            content: Content to flash.
            style: A semantic style.
            duration: Duration in seconds of the flash, or `None` to use default in settings.
        """
        self.query_one(Flash).flash(content, duration=duration, style=style)

    def scroll_to_latest_message(self):
        container = self.chat_container
        container.refresh()
        container.scroll_end(animate=False, force=True)

    @on(Prompt.CursorEscapingTop)
    async def on_cursor_up_from_prompt(self, event: Prompt.CursorEscapingTop) -> None:
        self.focus_latest_message()

    @on(Chatbox.CursorEscapingBottom)
    def move_focus_to_prompt(self) -> None:
        self.query_one(Prompt).focus()

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
