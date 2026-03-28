from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from textual.app import App
from textual.binding import Binding, BindingType

from byte.tui.screens.chat_screen import ChatScreen

if TYPE_CHECKING:
    from byte import Application


class ByteTUI(App, inherit_bindings=False):
    CSS_PATH = Path(__file__).parent / "tui.scss"
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

    # def compose(self):
    #     # Your UI widgets here
    #     yield RichLog()
    #     yield Input(placeholder="")

    async def on_mount(self):
        # Boot the application if not already booted
        if not self.byte_app.is_booted():
            await self.byte_app.boot()

        await self.push_screen(ChatScreen())
