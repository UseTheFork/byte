from typing import TYPE_CHECKING, Literal

from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.reactive import reactive
from textual.widgets import Rule, Static

if TYPE_CHECKING:
    from byte.tui import ByteTUI


LOADING_EMOJIS = [
    "[$primary](⁠[/]  [$primary]^[/][$secondary]⁠‿[/]⁠[$primary]^[/][$primary]⁠)[/]",
    "[$primary](⁠[/]  [$primary]^[/][$primary]⁠‿[/]⁠[$secondary]^[/][$primary]⁠)[/]",
    "[$primary](⁠[/]  [$primary]^[/][$primary]⁠‿[/]⁠[$primary]^[/][$secondary]⁠)[/]",
    "[$secondary](⁠[/]  [$primary]^[/][$primary]⁠‿[/]⁠[$primary]^[/][$primary]⁠)[/]",
    "[$primary](⁠[/]  [$secondary]^[/][$primary]⁠‿[/]⁠[$primary]^[/][$primary]⁠)[/]",
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
    "default": "[$primary](⁠  ^⁠‿⁠^⁠)[/]",
    "error": "[$error](-_-メ)[/]",
    "success": "(⁠ ⁠◕⁠‿⁠◕⁠)",
    "warning": "(⁠ ⁠°⁠▽⁠°⁠)",
    "info": "(⁠ ⁠ꈍ⁠ᴗ⁠ꈍ⁠)",
    "question": "[$secondary]┐⁠(⁠  -_⁠-⁠)⁠┌[/]",
}


class LoadingEmoji(Static):
    """Animated emoji that cycles through LOADING_EMOJIS."""

    DEFAULT_CSS = """
    LoadingEmoji {
        width: auto;
        padding-right: 1;
    }
    """

    emoji_index: reactive[int] = reactive(0)

    def _cycle_emoji(self) -> None:
        self.emoji_index = (self.emoji_index + 1) % len(LOADING_EMOJIS)

    def on_mount(self) -> None:
        self._timer = self.set_interval(0.1, self._cycle_emoji)

    def watch_emoji_index(self, index: int) -> None:
        self.update(LOADING_EMOJIS[index])

    def render(self):
        return LOADING_EMOJIS[self.emoji_index]


class StatusEmoji(Static):
    """Non-animated emoji that displays a static kaomoji based on the current state."""

    app: ByteTUI

    DEFAULT_CSS = """
    StatusEmoji {
        width: auto;
        padding-right: 1;
    }
    """

    state: reactive[StatusState] = reactive("default")

    def watch_state(self, state: StatusState) -> None:
        self.app.byte["log"].info(state)
        self.update(BYTE_STATES.get(state, BYTE_STATES["default"]))

    def render(self):
        return BYTE_STATES.get(self.state, BYTE_STATES["default"])


class StatusBar(HorizontalGroup, can_focus=False):
    """A status bar widget with either an animated loading emoji or a static status emoji,
    a message, and a rule.

    Use `show_loading(text)` to display the animated loading state.
    Use `show_status(text, state)` to display a static status emoji.
    Use `hide()` to hide the bar.

    Example (loading):
        ( o_゜)  Processing...  ──────────
    Example (status):
        (-_-メ)  Error occurred  ──────────
    """

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
        if text:
            self.text = text
        self.is_loading = True

    def show_status(self, text: str = "", state: StatusState = "default") -> None:
        """Show the status bar with a static status emoji."""
        if text:
            self.text = text
        self.is_loading = False
        self.query_one(StatusEmoji).state = state

    def watch_is_loading(self, loading: bool) -> None:
        try:
            self.query_one(LoadingEmoji).display = loading
            self.query_one(StatusEmoji).display = not loading
        except Exception:
            pass

    def watch_text(self, text: str) -> None:
        try:
            label = self.query_one("#status-label", Static)
            label.update(text)
        except Exception:
            pass

    def compose(self) -> ComposeResult:
        loading_emoji = LoadingEmoji()
        loading_emoji.display = False
        yield loading_emoji
        yield StatusEmoji()
        yield Static(self.text, id="status-label")
        yield Rule()
