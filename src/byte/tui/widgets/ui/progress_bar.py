from typing import Optional

from rich.console import RenderableType
from rich.progress_bar import ProgressBar as RichProgressBar
from textual.widget import Widget


class ProgressBar(Widget):
    """A progress bar widget that uses Rich's Progress for rendering.

    This widget extends Textual's Static but uses Rich's Progress
    rendering system for more advanced progress bar visualization.

    Example:
        progress = ProgressBar(total=100)
        progress.update(progress=50)
    """

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
        """Initialize the Rich progress bar.

        Args:
            total: Total number of steps for the progress bar
            name: The name of the widget
            id: The ID of the widget in the DOM
            classes: The CSS classes for the widget
            disabled: Whether the widget is disabled
        """
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
        """Render the progress bar using Rich's Progress.

        Returns:
            Rich Progress renderable
        """
        return self._progress

    def update(self, *, completed: float, total: Optional[float] = None) -> None:
        """Update the progress bar.

        Args:
            total: New total value
            progress: New progress value
            advance: Amount to advance progress by
        """
        # Update Rich progress task
        total = total if total is not None else self._progress.total
        self._progress.update(completed=completed, total=total)

        self.refresh()
