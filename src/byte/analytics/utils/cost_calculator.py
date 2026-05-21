from byte.analytics.schemas import LastMessageUsage, ModelUsage
from byte.llm.schemas import ModelConstraints


class CostCalculator:
    """Utility class for calculating LLM token costs.

    All cost calculations use the per-million token pricing model: each token
    cost field on ``ModelConstraints`` is expressed as cost-per-token and is
    divided by 1,000,000 to arrive at the actual dollar amount.
    """

    _PER_MILLION: int = 1_000_000

    @staticmethod
    def model_cost(usage: ModelUsage, constraints: ModelConstraints) -> float:
        """Calculate the total cost for a model's cumulative token usage.

        Args:
            usage: Aggregated token usage for the model across the session.
            constraints: Pricing constraints for the model.

        Returns:
            Cost in USD.
        """
        c = constraints
        return (
            usage.total.input_cache_read * c.cache_read_input_token_cost
            + usage.total.input_cache_creation * c.cache_write_input_token_cost
            + (usage.total.input - usage.total.input_cache_read) * c.input_cost_per_token
            + usage.total.output * c.output_cost_per_token
        ) / CostCalculator._PER_MILLION

    @staticmethod
    def message_cost(last_usage: LastMessageUsage, constraints: ModelConstraints) -> float:
        """Calculate the cost for a single message's token usage.

        Args:
            last_usage: Token usage from the most recent message.
            constraints: Pricing constraints for the model.

        Returns:
            Cost in USD.
        """
        c = constraints
        return (
            last_usage.input_cache_read * c.cache_read_input_token_cost
            + last_usage.input_cache_creation * c.cache_write_input_token_cost
            + (last_usage.input - last_usage.input_cache_read) * c.input_cost_per_token
            + last_usage.output * c.output_cost_per_token
        ) / CostCalculator._PER_MILLION
