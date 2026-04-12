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

        & Label {
            color: $primary;
            width: auto;
        }
    }
    """

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
        """ """
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.spinner_size = size

    def compose(self) -> ComposeResult:
        yield RuneSpinner(self.spinner_size)
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
