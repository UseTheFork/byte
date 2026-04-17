from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from textual import getters
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.widgets import Footer

from byte import CommandRegistryService, EventBus
from byte.system import SystemEvents
from byte.tui.themes import ThemeRegistry
from byte.tui.widgets.bootbox import Bootbox
from byte.tui.widgets.conversation import Conversation

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

    conversation = getters.query_one(Conversation)

    def __init__(self, app: Application):
        self.container = app
        self.command_registry = app.make(CommandRegistryService)
        self.event_bus = self.byte.make(EventBus)
        self.current_chatbox = None
        super().__init__()

    @property
    def byte(self) -> Application:
        if self.app.container is None:  # ty:ignore[unresolved-attribute]
            raise RuntimeError("Byte application is not initialized")
        return self.app.container  # ty:ignore[unresolved-attribute]

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
        self.conversation.chat_container.mount(response_chatbox)
