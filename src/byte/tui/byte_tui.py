from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import VerticalScroll
from textual.widgets import Footer

from byte import EventBus, Events
from byte.tui import Messages
from byte.tui.themes import ThemeRegistry
from byte.tui.widgets.agent_is_typing import ResponseStatus
from byte.tui.widgets.bootbox import Bootbox
from byte.tui.widgets.box.human_message_box import HumanMessageBox
from byte.tui.widgets.conversation import Conversation

if TYPE_CHECKING:
    from byte import Application


class ByteTUI(App, inherit_bindings=False):
    AUTO_FOCUS = "Conversation Prompt TextArea"

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
        self.container = container

        super().__init__()

    @property
    def chat_container(self) -> VerticalScroll:
        return self.query_one("#chat-container", VerticalScroll)

    @property
    def byte(self) -> Application:
        if self.app.container is None:  # ty:ignore[possibly-missing-attribute]
            raise RuntimeError("Byte application is not initialized")
        return self.app.container  # ty:ignore[possibly-missing-attribute]

    def compose(self) -> ComposeResult:
        yield Conversation()
        yield Footer()

    def _setup_themes(self):
        theme_registry = ThemeRegistry()
        theme_registry.register_themes(self)

        # TODO: This should come from config
        self.theme = "byte-catppuccin-mocha"

    async def on_mount(self):
        # Boot the application if not already booted
        if not self.byte.is_booted():
            await self.byte.boot()

        self._setup_themes()

        # TODO: This should not be here I think.
        event_bus = self.byte.make(EventBus)

        # Emit our post boot message to gather all needed info.
        payload = await event_bus.emit(Events.PostBoot(messages=[]))
        messages = payload.messages

        styled_logo = []
        logo_lines = [
            "░       ░░░  ░░░░  ░░        ░░        ░",
            "▒  ▒▒▒▒  ▒▒▒  ▒▒  ▒▒▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒▒▒▒",
            "▓       ▓▓▓▓▓    ▓▓▓▓▓▓▓  ▓▓▓▓▓      ▓▓▓",
            "█  ████  █████  ████████  █████  ███████",
            "█       ██████  ████████  █████        █",
        ]

        for row_idx, line in enumerate(logo_lines):
            styled_line = ""
            for col_idx, char in enumerate(line):
                # Calculate diagonal position (0.0 = top-left, 1.0 = bottom-right)
                diagonal_progress = (row_idx + col_idx) / (len(logo_lines) + len(line) - 2)

                # Use primary for first half, secondary for second half of diagonal
                if diagonal_progress < 0.5:
                    styled_line += f"[$primary]{char}[/$primary]"
                else:
                    styled_line += f"[$secondary]{char}[/$secondary]"

            # Fill remaining width with the last character
            logo_width = len(line)
            remaining_width = self.size.width - logo_width - 20

            if remaining_width > 0:
                last_char = line[-1] if line else " "
                last_diagonal_progress = (row_idx + len(line) - 1) / (len(logo_lines) + len(line) - 2)
                style = "$primary" if last_diagonal_progress < 0.5 else "$secondary"
                styled_line += f"[{style}]{last_char * remaining_width}[/{style}]"

            styled_logo.append(styled_line)

        response_chatbox = Bootbox("\n".join(styled_logo) + "\n\n" + "\n".join(messages))
        self.chat_container.mount(response_chatbox)

    @on(Messages.UserInputChanged)
    async def on_user_input_changed(self, event: Messages.UserInputChanged) -> None:
        """"""
        self.app.byte["log"].info("UserInputChanged")
        self.app.byte["log"].info(event)

    @on(Messages.UserInputSubmitted)
    async def new_user_message(self, event: Messages.UserInputSubmitted) -> None:
        """Handle a new user message."""
        self.query_one(Conversation).allow_input_submit = False

        user_message_chatbox = HumanMessageBox(event.body)
        self.chat_container.mount(user_message_chatbox)

        event_bus = self.byte.make(EventBus)
        # Emit our post boot message to gather all needed info.
        payload = await event_bus.emit(Events.UserInputSubmitted(messages=event.body))

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
