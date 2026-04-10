from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import VerticalGroup
from textual.reactive import reactive
from textual.widgets import Label, ProgressBar

from byte.tui.widgets.ui.loading_indicator import LoadingIndicator

if TYPE_CHECKING:
    from byte.tui import ByteTUI


class Linting(VerticalGroup):
    """A widget that displays linting progress and results."""

    DEFAULT_CSS = """
    Linting {
        height: auto;
        background: transparent;
        
        & LoadingIndicator {
            height: 1;
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
    file_count: reactive[int] = reactive(0)
    command_count: reactive[int] = reactive(0)
    current_file: reactive[str] = reactive("")
    completed: reactive[int] = reactive(0)
    total: reactive[int] = reactive(0)
    is_active: reactive[bool] = reactive(False)

    def __init__(
        self,
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

    def compose(self) -> ComposeResult:
        yield LoadingIndicator()
        yield ProgressBar(total=100, show_eta=False)
        yield Label("")

    def start_linting(self, file_count: int, command_count: int) -> None:
        """Start linting operation.

        Args:
            file_count: Number of files being linted
            command_count: Number of lint commands to execute
        """
        self.file_count = file_count
        self.command_count = command_count
        self.is_active = True
        self.completed = 0
        self.total = file_count * command_count

        # Show loading indicator
        loading = self.query_one(LoadingIndicator)
        loading.show("Linting")

        # Initialize progress bar
        progress = self.query_one(ProgressBar)
        progress.update(total=self.total, progress=0)

        # Update status label
        label = self.query_one(Label)
        label.update(f"Linting {file_count} files with {command_count} commands...")

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
        progress.update(progress=completed)

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
        loading = self.query_one(LoadingIndicator)
        loading.hide()

        # Update progress bar to complete
        progress = self.query_one(ProgressBar)
        progress.update(progress=self.total)

        # Update status label with results
        label = self.query_one(Label)
        if success:
            label.update(f"✓ Linting complete: {total_files} files processed, no errors")
        else:
            label.update(f"✗ Linting complete: {failed_files}/{total_files} files with errors")
