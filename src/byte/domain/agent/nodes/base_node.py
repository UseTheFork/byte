from abc import ABC

from langchain_core.messages import AIMessage
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime

from byte.core.mixins.bootable import Bootable
from byte.core.mixins.configurable import Configurable
from byte.core.mixins.eventable import Eventable
from byte.domain.agent.schemas import AssistantContextSchema, TokenUsageSchema
from byte.domain.agent.state import BaseState
from byte.domain.analytics.service.agent_analytics_service import AgentAnalyticsService


class Node(ABC, Bootable, Configurable, Eventable):
    async def _track_token_usage(self, result: AIMessage, mode: str) -> None:
        """Track token usage from AI response and update analytics.

        Extracts usage metadata from the AI message and records it in the
        analytics service based on the current AI mode (main or weak).

        Args:
                result: The AI message containing usage metadata
                mode: The AI mode being used ("main" or "weak")

        Usage: `await self._track_token_usage(result, runtime.context.mode)`
        """
        if result.usage_metadata:
            usage_metadata = result.usage_metadata
            usage = TokenUsageSchema(
                input_tokens=usage_metadata.get("input_tokens", 0),
                output_tokens=usage_metadata.get("output_tokens", 0),
                total_tokens=usage_metadata.get("total_tokens", 0),
            )
            agent_analytics_service = await self.make(AgentAnalyticsService)
            if mode == "main":
                await agent_analytics_service.update_main_usage(usage)
            else:
                await agent_analytics_service.update_weak_usage(usage)

    async def __call__(self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]):
        pass
