from typing import Any, List

from byte.analytics.schemas import LastMessageUsage, ModelUsage
from byte.llm.schemas import ModelConstraints


class UsageMetrics:
    """Utility class for calculating LLM usage metrics.

    All cost calculations use the per-million token pricing model: each token
    cost field on ``ModelConstraints`` is expressed as cost-per-token and is
    divided by 1,000,000 to arrive at the actual dollar amount.
    """

    _PER_MILLION: int = 1_000_000
    _DEFAULT_MAX_TOKENS: int = 150_000

    # Characters-per-token approximation used for prompt size estimation
    _CHARS_PER_TOKEN: int = 4

    @staticmethod
    def estimate_prompt_tokens(
        agent_state: dict, scratch_messages: List[Any], max_tokens: int = 150_000
    ) -> tuple[float, float]:
        """Estimate token usage for the current prompt and return memory utilisation.

        Uses a characters-per-token approximation (``len / 4``) across the
        assembled message strings and any scratch messages.

        Args:
            agent_state: Dict produced by ``PromptAssembler.generate_messages()``,
                expected keys: ``user_message``, ``system_message``, ``context_message``.
            scratch_messages: List of scratch messages from state; each must expose
                a ``text`` attribute.
            max_tokens: Context-window size to measure against. Defaults to
                ``_DEFAULT_MAX_TOKENS`` (150 000).

        Returns:
            Tuple of ``(total_tokens, memory_percent)`` where *memory_percent*
            is ``(total_tokens / max_tokens) * 100``.
        """
        total_tokens = (
            len(agent_state.get("user_message", "")) / UsageMetrics._CHARS_PER_TOKEN
            + len(agent_state.get("system_message", "")) / UsageMetrics._CHARS_PER_TOKEN
            + len(agent_state.get("context_message", "")) / UsageMetrics._CHARS_PER_TOKEN
            + sum(len(m.text) / UsageMetrics._CHARS_PER_TOKEN for m in scratch_messages)
        )
        memory_percent = (total_tokens / max_tokens) * 100
        return total_tokens, memory_percent

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
        ) / UsageMetrics._PER_MILLION

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
        ) / UsageMetrics._PER_MILLION
