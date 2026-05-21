from typing import TYPE_CHECKING, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import VerticalGroup
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer, Label

from byte.analytics import AgentAnalyticsService
from byte.llm import LLMRegistryService

if TYPE_CHECKING:
    from byte.tui import ByteTUI


class UsageAnalyticsScreen(ModalScreen[None]):
    """Modal screen displaying per-model token usage and calculated costs."""

    app: ByteTUI

    DEFAULT_CSS = """
        UsageAnalyticsScreen {
            align: center middle;
            background: $background 60%;

            & VerticalGroup {
                padding: 0 1;
                width: 90%;
                height: auto;
                border: thick $background 80%;
                background: $surface;

                & Label {
                    width: 1fr;
                    padding: 1 0 0 0;
                    text-style: bold;
                    color: $text-muted;
                }

                & DataTable {
                    height: auto;
                    max-height: 20;
                }

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
            "Dismiss",
            tooltip="Close this screen.",
            show=True,
            priority=True,
        ),
    ]

    def compose(self) -> ComposeResult:
        yield VerticalGroup(
            Label("Usage by Model"),
            DataTable(cursor_type="row"),
            Footer(show_command_palette=False),
        )

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.focus()
        table.add_columns(
            "Model",
            "Input Tokens",
            "Cache Read",
            "Cache Write",
            "Output Tokens",
            "Cost",
        )

        analytics_service = self.app.byte.make(AgentAnalyticsService)
        llm_registry = self.app.byte.make(LLMRegistryService)

        for model_id, usage in analytics_service.usage.by_model.items():
            model_data = llm_registry.get_model(model_id)
            cost = 0.0
            if model_data:
                c = model_data.constraints
                cost = (
                    usage.total.input_cache_read * c.cache_read_input_token_cost
                    + usage.total.input_cache_creation * c.cache_write_input_token_cost
                    + (usage.total.input - usage.total.input_cache_read) * c.input_cost_per_token
                    + usage.total.output * c.output_cost_per_token
                ) / 1_000_000

            table.add_row(
                model_id,
                f"{usage.total.input:,}",
                f"{usage.total.input_cache_read:,}",
                f"{usage.total.input_cache_creation:,}",
                f"{usage.total.output:,}",
                f"${cost:.6f}",
            )

    def action_dismiss_screen(self) -> None:
        self.dismiss()
