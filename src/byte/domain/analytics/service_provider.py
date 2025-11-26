from typing import List, Type

from byte.container import Container
from byte.core.event_bus import EventBus, EventType
from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.analytics.service.agent_analytics_service import AgentAnalyticsService


class AnalyticsProvider(ServiceProvider):
    """Service provider for agent analytics and usage tracking.

    Registers analytics service and configures event listeners to track
    agent usage, token consumption, and performance metrics. Provides
    real-time usage panels and persistent analytics data.
    Usage: Register with container to enable analytics tracking and display
    """

    def services(self) -> List[Type[Service]]:
        return [AgentAnalyticsService]

    async def boot(self, container: Container):
        """Boot analytics services and register event listeners.

        Sets up hooks to display usage panels before prompts and update
        analytics after agent completions, enabling real-time monitoring.
        Usage: `provider.boot(container)` -> analytics tracking becomes active
        """

        # Set up event listener for PRE_PROMPT_TOOLKIT
        event_bus = await container.make(EventBus)
        agent_analytics_service = await container.make(AgentAnalyticsService)

        # Register listener to show analytics panel before each prompt
        event_bus.on(
            EventType.PRE_PROMPT_TOOLKIT.value,
            agent_analytics_service.usage_panel_hook,
        )
