from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.reactive import Reactive, reactive
from textual.widgets import Label

from byte.tui.widgets.ui.rune_spinner import RuneSpinner


class LoadingIndicator(HorizontalGroup):
    """A widget that displays a loading spinner with a customizable message."""

    DEFAULT_CSS = """
    LoadingIndicator {
        height: 1;

        & .is-hidden {
            display:none;
        }

        & Label {
            color: $primary;
            width: auto;
        }
    }
    """

    hidden: Reactive[bool] = reactive(True)

    message: Reactive[str] = reactive("Thinking", recompose=True)
    spinner_size: Reactive[int] = reactive(8)

    def __init__(
        self,
        size: int = 8,
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
        self.spinner_size = size

    def compose(self) -> ComposeResult:
        """Compose the loading indicator with spinner and message label."""
        yield RuneSpinner(self.spinner_size)
        yield Label(f"{self.message}", classes="pl-1")

    def watch_hidden(self, hidden: bool) -> None:
        """Toggle the hidden CSS class based on hidden state."""
        self.set_class(hidden, "is-hidden")

    def watch_message(self, message: str) -> None:
        """Show the indicator and refresh layout when message changes."""
        self.hidden = False
        self.refresh(layout=True)
