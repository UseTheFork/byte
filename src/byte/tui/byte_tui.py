from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.widgets import Footer

from byte import CommandRegistryService, EventBus
from byte.tui.screens.conversation_screen import ConversationScreen
from byte.tui.themes.tui_theme_regisrty import TuiThemeRegistry
from byte.tui.widgets.conversation import Conversation

if TYPE_CHECKING:
    from byte import Application


class ByteTUI(App, inherit_bindings=False):
    AUTO_FOCUS = "PromptTextArea"

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
    ]

    SCREENS = {"conversation": ConversationScreen}

    ALLOW_IN_MAXIMIZED_VIEW = ""

    PAUSE_GC_ON_SCROLL = True

    def __init__(self, app: Application):
        self.container = app
        self.command_registry = app.make(CommandRegistryService)
        self.event_bus = self.byte.make(EventBus)
        super().__init__()

    @property
    def byte(self) -> Application:
        if self.app.container is None:  # ty:ignore[unresolved-attribute]
            raise RuntimeError("Byte application is not initialized")
        return self.app.container  # ty:ignore[unresolved-attribute]

    @property
    def conversation(self) -> Conversation:
        conversation = self.screen.query_one(Conversation)
        return conversation

    def compose(self) -> ComposeResult:
        yield Conversation()
        yield Footer()

    def _setup_themes(self):
        theme_registry = TuiThemeRegistry()
        theme_registry.register_themes(self)

        # TODO: This should come from config
        self.theme = "byte-catppuccin-mocha"

        # TODO: we need to also create a Rich theme and store it to keep things looking the same.

    async def on_mount(self):
        # Boot the application if not already booted
        if not self.byte.is_booted():
            await self.byte.boot()

        self._setup_themes()

        await self.push_screen("conversation")
