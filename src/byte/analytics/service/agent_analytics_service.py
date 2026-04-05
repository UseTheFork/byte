from byte import Events, Service
from byte.analytics import UsageAnalytics
from byte.orchestration import TokenUsageSchema
from byte.tui import TuiEvents


class AgentAnalyticsService(Service):
    """Service for tracking and displaying AI agent analytics and token usage.

    Monitors token consumption across different models and provides visual feedback
    to users about their usage patterns and limits through rich progress displays.
    """

    def boot(self):
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
        await self.calculate_analytics()

    async def update_weak_usage(self, token_usage: TokenUsageSchema) -> None:
        self.usage.weak.total.input += token_usage.input_tokens
        self.usage.weak.total.output += token_usage.output_tokens
        self.usage.last.input = token_usage.input_tokens
        self.usage.last.output = token_usage.output_tokens
        self.usage.last.type = "weak"
        await self.calculate_analytics()

    def get_cost_per_token(self, cost) -> float:
        return cost / 1000000

    async def calculate_analytics(self):
        """Calculate current analytics metrics for token usage and costs.

        Returns:
            Dictionary containing tokens_sent, tokens_received, message_cost,
            session_cost, and memory_percent.

        Usage: `analytics = await service.calculate_analytics()`
        """
        from byte.llm import LLMService

        llm_service = self.app.make(LLMService)

        # Calculate usage percentages
        memory_percent = min(
            (self.usage.main.context / llm_service._main_schema.constraints.max_input_tokens) * 100,
            100,
        )

        # Calculate weak model cost
        weak_cost = (
            self.usage.weak.total.input
            * self.get_cost_per_token(llm_service._weak_schema.constraints.input_cost_per_token)
        ) + (
            self.usage.weak.total.output
            * self.get_cost_per_token(llm_service._weak_schema.constraints.output_cost_per_token)
        )

        # Calculate main model cost
        main_cost = (
            self.usage.main.total.input
            * self.get_cost_per_token(llm_service._main_schema.constraints.input_cost_per_token)
        ) + (
            self.usage.main.total.output
            * self.get_cost_per_token(llm_service._main_schema.constraints.output_cost_per_token)
        )

        session_cost = main_cost + weak_cost

        # Calculate last message cost based on which model type was used
        last_message_type = self.usage.last.type
        if last_message_type == "main":
            last_message_cost = (
                self.usage.last.input
                * self.get_cost_per_token(llm_service._main_schema.constraints.input_cost_per_token)
            ) + (
                self.usage.last.output
                * self.get_cost_per_token(llm_service._main_schema.constraints.output_cost_per_token)
            )
        elif last_message_type == "weak":
            last_message_cost = (
                self.usage.last.input
                * self.get_cost_per_token(llm_service._weak_schema.constraints.input_cost_per_token)
            ) + (
                self.usage.last.output
                * self.get_cost_per_token(llm_service._weak_schema.constraints.output_cost_per_token)
            )
        else:
            last_message_cost = 0.0

        await self.emit(
            Events.TuiEvent(
                TuiEvents.UpdateAnalytics(
                    tokens_sent=self.usage.last.input,
                    tokens_received=self.usage.last.output,
                    message_cost=last_message_cost,
                    session_cost=session_cost,
                    memory_percent=memory_percent,
                )
            )
        )

    #     grid = Table.grid(expand=True)
    #     grid.add_column()
    #     grid.add_column(ratio=1)
    #     grid.add_column()
    #     grid.add_row("Memory Used ", progress, f" {main_percentage:.1f}%")

    #     grid_cost = Table.grid(expand=True)
    #     grid_cost.add_column()
    #     grid_cost.add_column(justify="right")
    #     grid_cost.add_row(
    #         f"Tokens: {last_input} sent, {last_output} received",
    #         f"Cost: ${last_message_cost:.2f} message, ${session_cost:.2f} session.",
    #     )

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
