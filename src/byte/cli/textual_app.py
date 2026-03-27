from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from textual.app import App
from textual.binding import Binding

from byte.cli.screens.chat_screen import ChatScreen

if TYPE_CHECKING:
    from byte import Application


class ByteTextualApp(App):
    ENABLE_COMMAND_PALETTE = False
    CSS_PATH = Path(__file__).parent / "tui.scss"
    BINDINGS = [
        Binding("q", "app.quit", "Quit", show=False),
        Binding("f1,?", "help", "Help"),
    ]

    def __init__(self, container: Application):
        self.byte = container

        super().__init__()

    # def compose(self):
    #     # Your UI widgets here
    #     yield RichLog()
    #     yield Input(placeholder="")

    async def on_mount(self):
        # Boot the application if not already booted
        if not self.byte.is_booted():
            await self.byte.boot()

        await self.push_screen(ChatScreen())
