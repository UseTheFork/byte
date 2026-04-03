from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from langchain.messages import AIMessageChunk
from textual import getters, on, work
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import VerticalScroll
from textual.widgets import Footer

from byte import Command, CommandRegistry, EventBus, Events
from byte.support.utils import extract_content_from_message
from byte.tui import Messages
from byte.tui.themes import ThemeRegistry
from byte.tui.widgets.agent.agent_response_panel import AgentResponsePanel
from byte.tui.widgets.bootbox import Bootbox
from byte.tui.widgets.box.human_message_box import HumanMessageBox
from byte.tui.widgets.conversation import Conversation
from byte.tui.widgets.prompt import Prompt

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

    prompt = getters.query_one("#prompt", Prompt)
    chat_container = getters.query_one("#chat-container", VerticalScroll)
    conversation = getters.query_one(Conversation)

    def __init__(self, container: Application):
        self.container = container
        self.command_registry = container.make(CommandRegistry)
        self.current_chatbox = None
        super().__init__()

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
        self.byte["log"].info("UserInputChanged")
        self.byte["log"].info(event)

    @on(Messages.UserInputSubmitted)
    async def new_user_message(self, event: Messages.UserInputSubmitted) -> None:
        """Handle a new user message."""
        self.query_one(Conversation).allow_input_submit = False

        user_message_chatbox = HumanMessageBox(event.body)
        await self.chat_container.mount(user_message_chatbox)
        self.conversation.scroll_to_latest_message()

        self.post_message(Messages.AgentResponseStarted())

        # Check if this is a slash command
        if event.body.startswith("/"):
            # Extract command without the slash
            command_text = event.body[1:]
            parts = command_text.split(" ", 1)
            command_name = parts[0]
            args = parts[1] if len(parts) > 1 else ""

            # Get the command from the registry
            command = self.command_registry.get_slash_command(command_name)

            if not command:
                pass

        self.current_chatbox = AgentResponsePanel()
        await self.chat_container.mount(self.current_chatbox)
        self.prompt.toggle_class("hidden")

        self.current_chatbox.heading.toggle_class("hidden")
        self.current_chatbox.heading.text = "Ask Agent"

        self.handle_command(command, args)

    @work(thread=True, group="handle_command")
    async def handle_command(self, command: Command, args: str) -> None:
        await command.handle(args, self.event_handler)

    async def event_handler(self, event) -> None:
        """Handle and dispatch events for this panel."""
        self.post_message(event)

    @on(Messages.AgentResponseStarted)
    def start_awaiting_response(self) -> None:
        """Prevent sending messages because the agent is typing."""
        pass
        # response_status = self.query_one(ResponseStatus)
        # response_status.set_agent_responding()
        # response_status.display = True

    @on(Messages.AgentResponseComplete)
    async def agent_response_complete(self, event: Messages.AgentResponseComplete) -> None:
        """Allow the user to send messages again."""
        self.prompt.toggle_class("hidden")
        self.conversation.scroll_to_latest_message()
        self.prompt.focus()
        self.current_chatbox = None

    @on(Messages.CommandStreamChunk)
    async def handle_stream_chunk(self, event: Messages.CommandStreamChunk) -> None:
        """Handle streaming chunks for this panel."""

        # TODO: This should be more graceful.
        assert self.current_chatbox

        # Update UI based on chunk type
        if event.chunk["type"] == "messages":
            message_chunk, metadata = event.chunk["data"]

            if isinstance(message_chunk, AIMessageChunk) and message_chunk.content:
                self.current_chatbox.rune_spinner.display = "none"

                msg = extract_content_from_message(message_chunk)
                self.current_chatbox.response += msg
                self.current_chatbox.agent_response_widget.update(self.current_chatbox.response)
                self.conversation.scroll_to_latest_message()

        elif event.chunk["type"] == "tasks":
            # await self._update_task_status(event.data)
            self.byte["log"].info(event.chunk)

    # @on(Messages.AgentResponseFailed)
    # @on(Messages.AgentResponseStarted)
    # @on(Messages.AgentResponseComplete)
