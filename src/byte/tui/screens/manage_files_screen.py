from typing import TYPE_CHECKING, ClassVar

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import VerticalGroup
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer

from byte.files import FileService

if TYPE_CHECKING:
    from byte.tui import ByteTUI


class ManageFilesScreen(ModalScreen[None]):
    """"""

    app: ByteTUI

    DEFAULT_CSS = """
        ManageFilesScreen {
            align: center middle;
            background: $background 60%;
            
            & VerticalGroup {
                padding: 0 1;
                width: 80%;
                height: auto;
                border: thick $background 80%;
                background: $surface;
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
    ]

    def compose(self) -> ComposeResult:
        yield VerticalGroup(
            DataTable(cursor_type="row"),
            Footer(),
        )

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.focus()
        table.add_columns("File", "Mode")

        file_service = self.app.byte.make(FileService)

        files = file_service.list_files()
        for file in files:
            table.add_row(file.relative_path, file.mode.value)

    @on(DataTable.RowSelected)
    async def handle_remove_file(self, event: DataTable.RowSelected) -> None:
        row = event.data_table.get_row(event.row_key)
        file_service = self.app.byte.make(FileService)
        result = await file_service.remove_file(str(row[0]))

        if result:
            event.data_table.remove_row(event.row_key)

    def action_dismiss_screen(self):
        self.dismiss()
