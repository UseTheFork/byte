from typing import List, Type

from byte.container import Container
from byte.core.event_bus import EventBus, EventType
from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.analytics.service.agent_analytics_service import AgentAnalyticsService


class AnalyticsProvider(ServiceProvider):
    """"""

    def services(self) -> List[Type[Service]]:
        return [AgentAnalyticsService]

    async def boot(self, container: Container):
        """"""

        # Set up event listener for PRE_PROMPT_TOOLKIT
        event_bus = await container.make(EventBus)
        agent_analytics_service = await container.make(AgentAnalyticsService)

        # Register listener to show analytics panel before each prompt
        event_bus.on(
            EventType.PRE_PROMPT_TOOLKIT.value,
            agent_analytics_service.display_usage_panel,
        )

        # Register listener to show analytics panel before each prompt
        event_bus.on(
            EventType.POST_AGENT_EXECUTION.value,
            agent_analytics_service.update_usage_analytics,
        )
