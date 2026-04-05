from __future__ import annotations

from typing import TYPE_CHECKING

from textual import getters, on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widget import Widget

from byte.tui.widgets.chatbox import Chatbox
from byte.tui.widgets.prompt.prompt_panel import PromptPanel

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

    chat_container = getters.query_one("#chat-container", VerticalScroll)

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
