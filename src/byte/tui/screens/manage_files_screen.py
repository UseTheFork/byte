from typing import TYPE_CHECKING, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import VerticalGroup
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer

from byte.files import FileMode, FileService

if TYPE_CHECKING:
    from byte.tui import ByteTUI


class ManageFilesScreen(ModalScreen[None]):
    """"""

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
            "s",
            "switch_mode",
            "Switch Mode",
            tooltip="Switch the file mode between read-only and editable.",
            show=True,
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
        yield VerticalGroup(
            DataTable(cursor_type="row"),
            Footer(show_command_palette=False),
        )

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.focus()
        self._col_file, self._col_mode = table.add_columns("File", "Mode")

        file_service = self.app.byte.make(FileService)
        files = file_service.list_files()
        for file in files:
            table.add_row(file.relative_path, file.mode.value)

    async def action_delete_row(self) -> None:
        table = self.query_one(DataTable)
        if table.cursor_row < 0:
            return

        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        row = table.get_row(row_key)
        file_service = self.app.byte.make(FileService)
        result = await file_service.remove_file(str(row[0]))

        if result:
            table.remove_row(row_key)

    async def action_switch_mode(self) -> None:
        table = self.query_one(DataTable)
        if table.cursor_row < 0:
            return

        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        row = table.get_row(row_key)
        file_path = str(row[0])

        file_service = self.app.byte.make(FileService)
        file_context = file_service.get_file_context(file_path)
        if file_context is None:
            return

        new_mode = FileMode.EDITABLE if file_context.mode == FileMode.READ_ONLY else FileMode.READ_ONLY
        result = await file_service.set_file_mode(file_path, new_mode)

        if result:
            # Column keys match the label strings passed to add_columns
            table.update_cell(row_key, self._col_mode, new_mode.value)

    def action_dismiss_screen(self):
        self.dismiss()
