from typing import TYPE_CHECKING, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import VerticalGroup
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer

from byte.files import FileService

if TYPE_CHECKING:
    from byte.tui import ByteTUI


class ManageFilesScreen(ModalScreen[None]):
    """Display and manage session files."""

    app: ByteTUI

    DEFAULT_CSS = """
        ManageFilesScreen {
            align: center middle;

            & VerticalGroup {
                padding: 0 1;
                width: 80%;
                height: auto;
                border: round $surface 80%;
                background: $surface;

                & Footer {
                    margin-top: 1;
                }
            }

        }
        """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding(
            "escape",
            "dismiss_screen",
            "Dismiss Screen",
            tooltip="Dismiss this screen.",
            show=True,
            priority=True,
        ),
        Binding(
            "d",
            "delete_row",
            "Delete File",
            tooltip="Remove the selected file from the context.",
            show=True,
        ),
    ]

    def compose(self) -> ComposeResult:
        """Compose the screen layout with data table and footer."""
        yield VerticalGroup(
            DataTable(cursor_type="row"),
            Footer(show_command_palette=False),
        )

    def on_mount(self) -> None:
        """Initialize the data table with files on mount."""
        table = self.query_one(DataTable)
        table.focus()
        self._col_file = table.add_columns("File")

        file_service = self.app.byte.make(FileService)
        files = file_service.list_files()
        for file in files:
            table.add_row(file.relative_path)

    async def action_delete_row(self) -> None:
        """Remove the selected file from context and table."""
        table = self.query_one(DataTable)
        if table.cursor_row < 0:
            return

        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        row = table.get_row(row_key)
        file_service = self.app.byte.make(FileService)
        result = await file_service.remove_file(str(row[0]))

        if result:
            table.remove_row(row_key)

    def action_dismiss_screen(self) -> None:
        """Dismiss the modal screen."""
        self.dismiss()
