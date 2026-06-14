from byte import Service
from byte.analytics import ModelUsage, UsageAnalytics, UsageMetrics
from byte.llm import LLMRegistryService
from byte.orchestration import TokenUsageSchema
from byte.tui import Messages


class AgentAnalyticsService(Service):
    """Track and display AI agent analytics and token usage."""

    def boot(self) -> None:
        """Initialize analytics service and register event listeners."""
        self.usage = UsageAnalytics()

    async def update_usage_by_model(self, model_id: str, token_usage: TokenUsageSchema) -> None:
        """Track token usage by model and aggregate by provider."""

        llm_registry = self.app.make(LLMRegistryService)
        model_data = llm_registry.get_model(model_id)
        if model_data:
            # Initialize provider entry if needed
            if model_id not in self.usage.by_model:
                self.usage.by_model[model_id] = ModelUsage()

            # Update provider's usage
            self.usage.by_model[model_id].total.input += token_usage.input_tokens
            self.usage.by_model[model_id].total.input_cache_read += token_usage.input_token_cache_read
            self.usage.by_model[model_id].total.input_cache_creation += token_usage.input_token_cache_creation
            self.usage.by_model[model_id].total.output += token_usage.output_tokens

            self.usage.last.input = token_usage.input_tokens
            self.usage.last.input_cache_read = token_usage.input_token_cache_read
            self.usage.last.input_cache_creation = token_usage.input_token_cache_creation
            self.usage.last.output = token_usage.output_tokens
            self.usage.last.type = model_id

            await self.calculate_analytics()

    async def calculate_analytics(self) -> None:
        """Calculate current analytics metrics for token usage and costs."""

        llm_registry = self.app.make(LLMRegistryService)

        # Calculate session cost across all models
        session_cost = 0.0
        for model_id, usage in self.usage.by_model.items():
            model_data = llm_registry.get_model(model_id)
            if model_data:
                session_cost += UsageMetrics.model_cost(usage, model_data.constraints)

        # Calculate last message cost based on model
        last_message_cost = 0.0
        if self.usage.last.type:
            model_data = llm_registry.get_model(self.usage.last.type)
            if model_data:
                last_message_cost = UsageMetrics.message_cost(self.usage.last, model_data.constraints)

        self.emit_tui(
            Messages.UpdateAnalytics(
                tokens_sent=self.usage.last.input,
                tokens_received=self.usage.last.output,
                message_cost=last_message_cost,
                session_cost=session_cost,
            )
        )

    def reset_usage(self) -> None:
        """Reset token usage counters to zero."""
        self.usage = UsageAnalytics()

    def reset_context(self) -> None:
        """Reset context token counters for all models."""
        for model_usage in self.usage.by_model.values():
            model_usage.context = 0
