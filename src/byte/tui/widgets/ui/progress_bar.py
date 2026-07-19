from rich.console import RenderableType
from rich.progress_bar import ProgressBar as RichProgressBar
from textual.widget import Widget


class ProgressBar(Widget):
    """Render the progress bar using Rich's Progress."""

    DEFAULT_CSS = """
    ProgressBar {
        height: 1;
        width: 100%;
    }
    """

    def __init__(
        self,
        total: float | None = 100,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialize the progress bar widget."""
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self._progress = RichProgressBar(
            total=total,
            complete_style="bar.complete",
        )

    def render(self) -> RenderableType:
        """Render the progress bar."""
        return self._progress

    def update(self, *, completed: float, total: float | None = None) -> None:
        """Update the progress bar with new values."""
        # Update Rich progress task
        total = total if total is not None else self._progress.total
        self._progress.update(completed=completed, total=total)

        self.refresh()
