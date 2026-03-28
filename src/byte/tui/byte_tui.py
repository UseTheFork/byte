from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import VerticalScroll
from textual.widgets import Footer

from byte.tui import Messages
from byte.tui.widgets.agent_is_typing import ResponseStatus
from byte.tui.widgets.bootbox import Bootbox
from byte.tui.widgets.conversation import Conversation

if TYPE_CHECKING:
    from byte import Application


class ByteTUI(App, inherit_bindings=False):
    AUTO_FOCUS = "Conversation Prompt HighlightedTextArea"

    CSS_PATH = Path(__file__).parent / "tui.tcss"
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding(
            "ctrl+q",
            "quit",
            "Quit",
            tooltip="Quit the app and return to the command prompt.",
            show=False,
            priority=True,
        ),
        Binding("ctrl+c", "help_quit", show=False, system=True),
        # Binding("ctrl+s", "sessions", "Sessions"),
        # Binding("f1", "toggle_help_panel", "Help", priority=True),
        Binding(
            "f2,ctrl+comma",
            "settings",
            "Settings",
            tooltip="Settings screen",
        ),
    ]

    ALLOW_IN_MAXIMIZED_VIEW = ""

    HORIZONTAL_BREAKPOINTS = [(0, "-narrow"), (100, "-wide")]

    PAUSE_GC_ON_SCROLL = True

    def __init__(self, container: Application):
        self.byte_app = container

        super().__init__()

    @property
    def chat_container(self) -> VerticalScroll:
        return self.query_one("#chat-container", VerticalScroll)

    def compose(self) -> ComposeResult:
        yield Conversation()
        yield Footer()

    async def on_mount(self):
        # Boot the application if not already booted
        if not self.byte_app.is_booted():
            await self.byte_app.boot()

        response_chatbox = Bootbox(
            message="test",
        )
        self.chat_container.mount(response_chatbox)

    @on(Messages.UserInputSubmitted)
    def new_user_message(self, event: Messages.UserInputSubmitted) -> None:
        """Handle a new user message."""
        self.query_one(Conversation).allow_input_submit = False

        response_status = self.query_one(ResponseStatus)
        response_status.set_awaiting_response()
        response_status.display = True

    @on(Messages.AgentResponseStarted)
    def start_awaiting_response(self) -> None:
        """Prevent sending messages because the agent is typing."""
        response_status = self.query_one(ResponseStatus)
        response_status.set_agent_responding()
        response_status.display = True

    @on(Messages.AgentResponseComplete)
    async def agent_response_complete(self, event: Messages.AgentResponseComplete) -> None:
        """Allow the user to send messages again."""
        self.query_one(ResponseStatus).display = False
        self.query_one(Conversation).allow_input_submit = True
        # log.debug(f"Agent response complete. Adding message to chat_id {event.chat_id!r}: {event.message}")
        # if self.chat_data.id is None:
        # raise RuntimeError("Chat has no ID. This is likely a bug in Elia.")

        # await self.chats_manager.add_message_to_chat(chat_id=self.chat_data.id, message=event.message)
