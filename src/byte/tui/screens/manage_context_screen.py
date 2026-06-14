from typing import TYPE_CHECKING, ClassVar

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import VerticalGroup
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer

from byte.knowledge import SessionContextService

if TYPE_CHECKING:
    from byte.tui import ByteTUI


class ManageContextScreen(ModalScreen[None]):
    """Display and manage session context items."""

    app: ByteTUI

    DEFAULT_CSS = """
        ManageContextScreen {
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
        """Compose the screen layout with data table and footer."""
        yield VerticalGroup(
            DataTable(cursor_type="row"),
            Footer(show_command_palette=False),
        )

    def on_mount(self) -> None:
        """Initialize the data table with session context items on mount."""
        table = self.query_one(DataTable)
        table.focus()
        table.add_columns("Key", "Type")

        session_context_service = self.app.byte.make(SessionContextService)

        all_context = session_context_service.get_all_context()
        for key, model in all_context.items():
            table.add_row(model.key, model.type)

    @on(DataTable.RowSelected)
    def handle_remove_context(self, event: DataTable.RowSelected) -> None:
        """Remove selected context item from session and table."""
        row = event.data_table.get_row(event.row_key)
        session_context_service = self.app.byte.make(SessionContextService)
        session_context_service.remove_context(row[0])

        event.data_table.remove_row(event.row_key)

    def action_dismiss_screen(self) -> None:
        """Dismiss the modal screen."""
        self.dismiss()
