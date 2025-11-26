from rich.console import Group
from rich.progress_bar import ProgressBar
from rich.table import Table

from byte.core.event_bus import Payload
from byte.core.service.base_service import Service
from byte.domain.agent.schemas import TokenUsageSchema
from byte.domain.analytics.schemas import UsageAnalytics
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.llm.service.llm_service import LLMService


class AgentAnalyticsService(Service):
    """Service for tracking and displaying AI agent analytics and token usage.

    Monitors token consumption across different models and provides visual feedback
    to users about their usage patterns and limits through rich progress displays.
    """

    async def boot(self):
        """Initialize analytics service and register event listeners.

        Sets up token tracking and registers the pre-prompt hook to display
        usage statistics before each user interaction.
        """
        self.usage = UsageAnalytics()

    async def update_main_usage(self, token_usage: TokenUsageSchema) -> None:
        self.usage.main.context = token_usage.total_tokens
        self.usage.main.total.input += token_usage.input_tokens
        self.usage.main.total.output += token_usage.output_tokens
        self.usage.last.input = token_usage.input_tokens
        self.usage.last.output = token_usage.output_tokens
        self.usage.last.type = "main"

    async def update_weak_usage(self, token_usage: TokenUsageSchema) -> None:
        self.usage.weak.total.input += token_usage.input_tokens
        self.usage.weak.total.output += token_usage.output_tokens
        self.usage.last.input = token_usage.input_tokens
        self.usage.last.output = token_usage.output_tokens
        self.usage.last.type = "weak"

    async def usage_panel_hook(self, payload: Payload) -> Payload:
        """Display token usage analytics panel with progress bars.

        Shows current token consumption for both main and weak models
        with visual progress indicators to help users track their usage.
        """
        console = await self.make(ConsoleService)
        llm_service = await self.make(LLMService)

        info_panel = payload.get("info_panel", [])

        # Calculate usage percentages
        main_percentage = min(
            (self.usage.main.context / llm_service._service_config.main.constraints.max_input_tokens) * 100,
            100,
        )

        weak_cost = (
            self.usage.weak.total.input * llm_service._service_config.weak.constraints.input_cost_per_token
        ) + (self.usage.weak.total.output * llm_service._service_config.weak.constraints.output_cost_per_token)

        main_cost = (
            self.usage.main.total.input * llm_service._service_config.main.constraints.input_cost_per_token
        ) + (self.usage.main.total.output * llm_service._service_config.main.constraints.output_cost_per_token)

        # llm_service._service_config.main.model

        progress = ProgressBar(
            total=llm_service._service_config.main.constraints.max_input_tokens,
            completed=self.usage.main.context,
            complete_style="success",
        )

        session_cost = main_cost + weak_cost

        # Calculate last message cost based on which model type was used
        last_message_type = self.usage.last.type
        if last_message_type == "main":
            last_message_cost = (
                self.usage.last.input * llm_service._service_config.main.constraints.input_cost_per_token
            ) + (self.usage.last.output * llm_service._service_config.main.constraints.output_cost_per_token)
        elif last_message_type == "weak":
            last_message_cost = (
                self.usage.last.input * llm_service._service_config.weak.constraints.input_cost_per_token
            ) + (self.usage.last.output * llm_service._service_config.weak.constraints.output_cost_per_token)
        else:
            last_message_cost = 0.0

        last_input = self.humanizer(self.usage.last.input)
        last_output = self.humanizer(self.usage.last.output)

        grid = Table.grid(expand=True)
        grid.add_column()
        grid.add_column(ratio=1)
        grid.add_column()
        grid.add_row("Memory Used ", progress, f" {main_percentage:.1f}%")

        grid_cost = Table.grid(expand=True)
        grid_cost.add_column()
        grid_cost.add_column(justify="right")
        grid_cost.add_row(
            f"Tokens: {last_input} sent, {last_output} received",
            f"Cost: ${last_message_cost:.2f} message, ${session_cost:.2f} session.",
        )

        analytics_panel = console.panel(
            Group(grid, grid_cost),
            title="Analytics",
        )

        info_panel.append(analytics_panel)
        return payload.set("info_panel", info_panel)

    def reset_usage(self):
        """Reset token usage counters to zero.

        Useful for starting fresh sessions or after reaching certain milestones.
        """
        self.usage = UsageAnalytics()

    def reset_context(self) -> None:
        """Reset context token counters for both main and weak models.

        Clears the current context usage while preserving total session usage.
        Useful when starting a new conversation or clearing the message history.
        """
        self.usage.main.context = 0
        self.usage.weak.context = 0

    def humanizer(self, number: int | float) -> str:
        divisor = 1
        for suffix in ("K", "M", "B", "T"):
            divisor *= 1000
            max_allowed = divisor * 1000
            quotient, remainder = divmod(number, divisor)
            if number > max_allowed:
                continue
            if quotient:
                break
            return str(number)
        if remaining := (remainder and round(remainder / divisor, 1)):
            quotient += remaining
        return f"{quotient}{suffix}"
