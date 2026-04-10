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
        & RuneSpinner {
            max-width: 8;
        }

        & Label {
            color: $primary;
            width: auto;
        }
    }
    """

    message: Reactive[str] = reactive("Thinking", recompose=True)

    def compose(self) -> ComposeResult:
        yield RuneSpinner()
        yield Label(f"{self.message}", classes="pl-1")

    def show(self, message: str = "Thinking") -> None:
        """Show the loading indicator with a custom message.

        Args:
            message: The message to display next to the spinner.
        """
        self.message = message
        self.remove_class("hidden")

    def hide(self) -> None:
        """Hide the loading indicator."""
        self.add_class("hidden")
