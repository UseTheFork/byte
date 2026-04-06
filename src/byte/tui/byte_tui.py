from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Literal

from textual import getters, on
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import VerticalScroll
from textual.widgets import Footer

from byte import CommandRegistryService, EventBus
from byte.system import SystemEvents
from byte.tui import TuiEvents
from byte.tui.messages import Messages
from byte.tui.themes import ThemeRegistry
from byte.tui.widgets.bootbox import Bootbox
from byte.tui.widgets.conversation import Conversation
from byte.tui.widgets.panels.human_message_panel import HumanMessagePanel
from byte.tui.widgets.panels.pending_panel import PendingPanel
from byte.tui.widgets.prompt.analytics import Analytics
from byte.tui.widgets.prompt.flash import Flash
from byte.tui.widgets.prompt.prompt_panel import PromptPanel
from byte.tui.widgets.ui.loading_indicator import LoadingIndicator

if TYPE_CHECKING:
    from byte import Application


class ByteTUI(App, inherit_bindings=False):
    AUTO_FOCUS = "Conversation PromptPanel PromptTextArea"

    CSS_PATH = [
        Path(__file__).parent / "utils.tcss",
        Path(__file__).parent / "tui.tcss",
    ]

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

    PAUSE_GC_ON_SCROLL = True

    prompt = getters.query_one("#prompt", PromptPanel)
    chat_container = getters.query_one("#chat-container", VerticalScroll)
    loading_indicator = getters.query_one(LoadingIndicator)
    conversation = getters.query_one(Conversation)

    def __init__(self, container: Application):
        self.container = container
        self.command_registry = container.make(CommandRegistryService)
        self.event_bus = self.byte.make(EventBus)
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
        payload = await event_bus.emit(SystemEvents.PostBoot(messages=[]))
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

    @on(Messages.UserInputSubmitted)
    async def new_user_message(self, event: Messages.UserInputSubmitted) -> None:
        """Handle a new user message."""
        self.query_one(Conversation).allow_input_submit = False

        user_message_chatbox = HumanMessagePanel(event.body)
        await self.chat_container.mount(user_message_chatbox)
        self.conversation.scroll_to_latest_message()

        # TODO: should we make this none blocking?
        await self.event_bus.emit(
            TuiEvents.UserInputSubmitted(
                event.body,
            )
        )

    async def mount_pending_response_panel(self) -> PendingPanel:
        """Handle and dispatch events for this panel."""
        agent_response_panel = PendingPanel()
        await self.chat_container.mount(agent_response_panel)

        self.chat_container.refresh(layout=True)

        return agent_response_panel

    def flash(
        self,
        content: str,
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

    def analytics(
        self,
        tokens_sent: int,
        tokens_received: int,
        message_cost: float,
        session_cost: float,
        memory_percent: float,
    ) -> None:
        """Update analytics display with token usage and cost information.

        Args:
            tokens_sent: Number of tokens sent in the last message.
            tokens_received: Number of tokens received in the last message.
            message_cost: Cost of the last message in dollars.
            session_cost: Total cost of the session in dollars.
            memory_percent: Percentage of memory used (0-100).
        """
        self.query_one(Analytics).update_analytics(
            tokens_sent=tokens_sent,
            tokens_received=tokens_received,
            message_cost=message_cost,
            session_cost=session_cost,
            memory_percent=memory_percent,
        )

    def update_files(self, editable: int, read_only: int) -> None:
        """Update file counts display with current context statistics.

        Args:
            editable: Number of editable files in context.
            read_only: Number of read-only files in context.
        """
        self.query_one(Analytics).update_files(editable=editable, read_only=read_only)

    @on(Messages.Answer)
    async def on_question_answered(self, event: Messages.Answer):
        # Just hide the question widget
        # Future is already resolved by the widget itself
        self.prompt.remove_class("-mode-ask")
        self.prompt.prompt_text_area.focus()
