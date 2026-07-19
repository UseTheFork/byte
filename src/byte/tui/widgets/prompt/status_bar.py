from typing import TYPE_CHECKING, Literal

from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.reactive import reactive
from textual.widgets import Rule, Static

from byte.tui.constants import (
    ACCENT_X,
    ARM_LEFT_BOX_DRAW,
    ARM_RIGHT_BOX_DRAW,
    EYE_CIRCUMFLEX,
    EYE_HYPHEN,
    EYE_KEP,
    L_PARENTHESIS,
    MOUTH_HALF_O,
    MOUTH_LOW_LINE,
    MOUTH_UNDERTIE,
    R_PARENTHESIS,
    SPACE,
    WORD_JOINER,
)

if TYPE_CHECKING:
    from byte.tui import ByteTUI

LOADING_EMOJIS = [
    f"[$primary]{L_PARENTHESIS}{WORD_JOINER}{SPACE}{SPACE}{SPACE}{EYE_CIRCUMFLEX}{MOUTH_UNDERTIE}{WORD_JOINER}{EYE_CIRCUMFLEX}{WORD_JOINER}{R_PARENTHESIS}[/][$primary].[/]｡oO",
    f"[$primary]{L_PARENTHESIS}{WORD_JOINER}{SPACE}{SPACE}{SPACE}{EYE_CIRCUMFLEX}{MOUTH_UNDERTIE}{WORD_JOINER}{EYE_CIRCUMFLEX}{WORD_JOINER}{R_PARENTHESIS}[/][$secondary].[/][$primary]｡[/]oO",
    f"[$primary]{L_PARENTHESIS}{WORD_JOINER}{SPACE}{SPACE}{SPACE}{EYE_CIRCUMFLEX}{MOUTH_UNDERTIE}{WORD_JOINER}{EYE_CIRCUMFLEX}{WORD_JOINER}{R_PARENTHESIS}[/].[$secondary]｡[/][$primary]o[/]O",
    f"[$primary]{L_PARENTHESIS}{WORD_JOINER}{SPACE}{SPACE}{SPACE}{EYE_CIRCUMFLEX}{MOUTH_UNDERTIE}{WORD_JOINER}{EYE_CIRCUMFLEX}{WORD_JOINER}{R_PARENTHESIS}[/].｡[$secondary]o[/][$primary]O[/]",
    f"[$primary]{L_PARENTHESIS}{WORD_JOINER}{SPACE}{SPACE}{SPACE}{EYE_CIRCUMFLEX}{MOUTH_UNDERTIE}{WORD_JOINER}{EYE_CIRCUMFLEX}{WORD_JOINER}{R_PARENTHESIS}[/].｡o[$secondary]O[/]",
]

StatusState = Literal[
    "default",
    "error",
    "success",
    "warning",
    "info",
    "question",
    "loading",
]

BYTE_STATES: dict[StatusState, str] = {
    "default": f"[$primary]{L_PARENTHESIS}{WORD_JOINER}{SPACE}{SPACE}{SPACE}{EYE_CIRCUMFLEX}{WORD_JOINER}{MOUTH_UNDERTIE}{WORD_JOINER}{EYE_CIRCUMFLEX}{WORD_JOINER}{R_PARENTHESIS}[/]",  # (⁠   ^⁠‿⁠^⁠)
    "error": f"[$error]{L_PARENTHESIS}{WORD_JOINER}{ACCENT_X}{SPACE}{EYE_HYPHEN}{WORD_JOINER}{MOUTH_LOW_LINE}{WORD_JOINER}{EYE_HYPHEN}{WORD_JOINER}{R_PARENTHESIS}[/]",  # (メ -_-)
    "success": "(⁠ ⁠◕⁠‿⁠◕⁠)",  # (⁠ ⁠◕⁠‿⁠◕⁠)
    "warning": "(⁠ ⁠°⁠▽⁠°⁠)",  # (⁠ ⁠°⁠▽⁠°⁠)
    "info": f"{L_PARENTHESIS}{WORD_JOINER}{SPACE}{SPACE}{SPACE}{EYE_KEP}{WORD_JOINER}{MOUTH_HALF_O}{WORD_JOINER}{EYE_KEP}{WORD_JOINER}{R_PARENTHESIS}",  # (⁠   ⁠ꈍ⁠ᴗ⁠ꈍ⁠)
    "question": f"[$secondary]{ARM_RIGHT_BOX_DRAW}{L_PARENTHESIS}{WORD_JOINER}{SPACE}{SPACE}{SPACE}{EYE_HYPHEN}{WORD_JOINER}{MOUTH_LOW_LINE}{WORD_JOINER}{EYE_HYPHEN}{WORD_JOINER}{R_PARENTHESIS}{ARM_LEFT_BOX_DRAW}[/]",  # ┐⁠(⁠  -_⁠-⁠)⁠┌
}


class LoadingEmoji(Static):
    """Cycle through animated loading emojis."""

    DEFAULT_CSS = """
    LoadingEmoji {
        width: auto;
        padding-right: 1;
    }
    """

    emoji_index: reactive[int] = reactive(0)

    def _cycle_emoji(self) -> None:
        """Cycle to the next emoji index."""
        self.emoji_index = (self.emoji_index + 1) % len(LOADING_EMOJIS)

    def on_mount(self) -> None:
        """Start the emoji cycling timer."""
        self._timer = self.set_interval(0.1, self._cycle_emoji)

    def watch_emoji_index(self, index: int) -> None:
        """Update the display with the current emoji."""
        self.update(LOADING_EMOJIS[index])

    def render(self) -> str:
        """Render the current emoji."""
        return LOADING_EMOJIS[self.emoji_index]


class StatusEmoji(Static):
    """Display a static status emoji based on the current state."""

    app: ByteTUI

    DEFAULT_CSS = """
    StatusEmoji {
        width: auto;
        padding-right: 1;
    }
    """

    state: reactive[StatusState] = reactive("default")

    def watch_state(self, state: StatusState) -> None:
        """Update the display with the new state emoji."""
        self.update(BYTE_STATES.get(state, BYTE_STATES["default"]))

    def render(self) -> str:
        """Render the current state emoji."""
        return BYTE_STATES.get(self.state, BYTE_STATES["default"])


class StatusBar(HorizontalGroup, can_focus=False):
    """Display a status bar with emoji, message, and rule."""

    DEFAULT_CSS = """
    StatusBar {
        height: 1;
        width: 1fr;
        padding-right: 1;

        & LoadingEmoji {
            width: auto;
            padding-right: 1;
        }
        & StatusEmoji {
            width: auto;
            padding-right: 1;
        }
        & Static {
            width: auto;
            padding-right: 1;
        }
        & Rule {
            width: 1fr;
        }
    }
    """

    text: reactive[str] = reactive("")
    is_loading: reactive[bool] = reactive(False)

    def __init__(
        self,
        text: str = "",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.text = text

    def show_loading(self, text: str = "") -> None:
        """Show the status bar in animated loading mode."""
        self.text = text
        self.is_loading = True

    def show_status(self, text: str = "", state: StatusState = "default") -> None:
        """Show the status bar with a static status emoji."""
        self.text = text
        self.is_loading = False
        self.query_one(StatusEmoji).state = state

    def update_text(self, text: str) -> None:
        """Update the text in the status bar."""
        self.text = text

    def watch_is_loading(self, loading: bool) -> None:
        """Update emoji display based on loading state."""
        try:
            self.query_one(LoadingEmoji).display = loading
            self.query_one(StatusEmoji).display = not loading
        except Exception:
            pass

    def watch_text(self, text: str) -> None:
        """Update the status label text."""
        try:
            label = self.query_one("#status-label", Static)
            label.update(text)
        except Exception:
            pass

    def compose(self) -> ComposeResult:
        """Compose the status bar with loading emoji, status emoji, label, and rule."""
        loading_emoji = LoadingEmoji()
        loading_emoji.display = False
        yield loading_emoji
        yield StatusEmoji()
        yield Static(self.text, id="status-label")
        yield Rule()
