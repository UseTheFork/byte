from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.reactive import reactive
from textual.widgets import Label, Markdown

from byte.tui.widgets.ui.progress_bar import ProgressBar
from byte.tui.widgets.ui.rune_spinner import RuneSpinner

if TYPE_CHECKING:
    from byte.tui import ByteTUI


class Linting(VerticalGroup):
    """A widget that displays linting progress and results."""

    BORDER_TITLE = "Lint"

    DEFAULT_CSS = """
    Linting {
        height: auto;
        background: transparent;
        
        & HorizontalGroup {
            height: 1;
            & RuneSpinner {
                width: 2;
            }
            
            & ProgressBar {
                width: 1fr;
            }
        }
        
        & ProgressBar {
            height: 1;
        }
        
        & Label {
            height: auto;
            width: 100%;
        }
    }
    """

    app: ByteTUI

    # Reactive properties for tracking state
    current_file: reactive[str] = reactive("")
    completed: reactive[int] = reactive(0)
    total: reactive[int] = reactive(0)
    is_active: reactive[bool] = reactive(False)

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str = "border-round-secondary",
        disabled: bool = False,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    def compose(self) -> ComposeResult:
        with HorizontalGroup():
            yield RuneSpinner(2)
            yield ProgressBar(total=100)
        yield Label("")
        yield Markdown("", classes="hidden", id="lint-results")

    def start_linting(self, total_commands: int) -> None:
        """Start linting operation.

        Args:
            total_commands: Total number of command executions
        """
        self.is_active = True
        self.completed = 0
        self.total = total_commands

        # Initialize progress bar
        progress = self.query_one(ProgressBar)
        progress.update(total=self.total, completed=0)

        # Update status label
        label = self.query_one(Label)
        label.update(f"Running {total_commands} lint commands...")

    def update_progress(self, current_file: str, completed: int, total: int) -> None:
        """Update linting progress.

        Args:
            current_file: Name of file currently being linted
            completed: Number of files completed
            total: Total number of files
        """
        self.current_file = current_file
        self.completed = completed
        self.total = total

        # Update progress bar
        progress = self.query_one(ProgressBar)
        progress.update(completed=completed)

        # Update status label
        label = self.query_one(Label)
        label.update(f"Linting: {current_file} ({completed}/{total})")

    def complete_linting(self, total_files: int, failed_files: int, success: bool) -> None:
        """Complete linting operation.

        Args:
            total_files: Total files processed
            failed_files: Number of files with lint errors
            success: Whether all lints passed (no errors)
        """
        self.is_active = False

        # Hide loading indicator
        loading = self.query_one(RuneSpinner)
        loading.add_class("hidden")

        # Update progress bar to complete
        progress = self.query_one(ProgressBar)
        progress.update(completed=self.total)
        progress.add_class("hidden")

        # Update status label with results
        label = self.query_one(Label)
        self.remove_class("border-round-secondary")
        if success:
            self.add_class("border-round-success")
            label.update(f"Linting complete: {total_files} files processed, no errors")
        else:
            self.add_class("border-round-error")
            label.update(f"Linting complete: {failed_files}/{total_files} files with errors")

    def display_results(self, content: str) -> None:
        """Display lint results in the markdown widget.

        Args:
            content: Formatted markdown content with lint results
        """
        results_widget = self.query_one("#lint-results", Markdown)
        results_widget.update(content)
        results_widget.remove_class("hidden")
