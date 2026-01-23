from typing import List, Type

from byte import EventBus, EventType, Service, ServiceProvider
from byte.analytics import AgentAnalyticsService


class AnalyticsProvider(ServiceProvider):
    """Service provider for agent analytics and usage tracking.

    Registers analytics service and configures event listeners to track
    agent usage, token consumption, and performance metrics. Provides
    real-time usage panels and persistent analytics data.
    Usage: Register with container to enable analytics tracking and display
    """

    def services(self) -> List[Type[Service]]:
        return [AgentAnalyticsService]

    async def boot(self):
        """Boot analytics services and register event listeners.

        Sets up hooks to display usage panels before prompts and update
        analytics after agent completions, enabling real-time monitoring.
        Usage: `provider.boot(container)` -> analytics tracking becomes active
        """

        # Set up event listener for PRE_PROMPT_TOOLKIT
        event_bus = self.app.make(EventBus)
        agent_analytics_service = self.app.make(AgentAnalyticsService)

        # Register listener to show analytics panel before each prompt
        event_bus.on(
            EventType.PRE_PROMPT_TOOLKIT.value,
            agent_analytics_service.usage_panel_hook,
        )
