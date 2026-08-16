from typing import TYPE_CHECKING, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import VerticalGroup
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer, Label

from byte.analytics import AgentAnalyticsService, UsageMetrics
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
        """Compose the screen layout with usage analytics table and footer."""
        yield VerticalGroup(
            Label("Usage by Model"),
            DataTable(cursor_type="row"),
            Footer(show_command_palette=False),
        )

    def on_mount(self) -> None:
        """Initialize the data table with per-model usage metrics on mount."""
        table = self.query_one(DataTable)
        table.focus()
        table.add_columns(
            "Provider",
            "Model",
            "Input Tokens",
            "Cache Read",
            "Cache Write",
            "Output Tokens",
            "Cost",
        )

        analytics_service = self.app.byte.make(AgentAnalyticsService)
        llm_registry = self.app.byte.make(LLMRegistryService)

        model_providers: dict[str, str] = getattr(analytics_service, "_model_providers", {})
        for model_id, usage in analytics_service.usage.by_model.items():
            provider = model_providers.get(model_id)
            cost = 0.0
            if provider:
                model_data = llm_registry.get_model(provider, model_id)
                if model_data:
                    cost = UsageMetrics.model_cost(usage, model_data.constraints)

            table.add_row(
                provider or "Unknown",
                model_id,
                f"{usage.total.input:,}",
                f"{usage.total.input_cache_read:,}",
                f"{usage.total.input_cache_creation:,}",
                f"{usage.total.output:,}",
                f"${cost:.2f}",
            )

    def action_dismiss_screen(self) -> None:
        """Dismiss the modal screen."""
        self.dismiss()
