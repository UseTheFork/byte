from abc import ABC, abstractmethod
from typing import Any

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime

from byte.core.mixins.bootable import Bootable
from byte.core.mixins.configurable import Configurable
from byte.core.mixins.eventable import Eventable
from byte.domain.agent.schemas import AssistantContextSchema, TokenUsageSchema
from byte.domain.agent.state import BaseState
from byte.domain.analytics.service.agent_analytics_service import AgentAnalyticsService


class Node(ABC, Bootable, Configurable, Eventable):
    async def _track_token_usage(self, usage_metadata: dict, mode: str) -> None:
        """Track token usage from callback metadata and update analytics.

        Extracts usage metadata from the get_usage_metadata_callback result
        and records it in the analytics service based on the current AI mode.

        Args:
            usage_metadata: Dictionary with model names as keys and usage stats as values
            mode: The AI mode being used ("main" or "weak")

        Usage: `await self._track_token_usage(cb, runtime.context.mode)`
        """
        if usage_metadata:
            # Get the first model's usage data (typically only one model)
            model_usage = next(iter(usage_metadata.values()))

            usage = TokenUsageSchema(
                input_tokens=model_usage.get("input_tokens", 0),
                output_tokens=model_usage.get("output_tokens", 0),
                total_tokens=model_usage.get("total_tokens", 0),
            )
            agent_analytics_service = await self.make(AgentAnalyticsService)
            if mode == "main":
                await agent_analytics_service.update_main_usage(usage)
            else:
                await agent_analytics_service.update_weak_usage(usage)

    @abstractmethod
    async def __call__(
        self,
        state: BaseState,
        *,
        runtime: Runtime[AssistantContextSchema],
        config: RunnableConfig,
    ) -> Any:
        """Execute the node logic. Must be implemented by subclasses."""
        pass
