from byte import ServiceProvider
from byte.analytics import AgentAnalyticsService


class AnalyticsProvider(ServiceProvider):
    """Service provider for agent analytics and usage tracking.

    Registers analytics service and configures event listeners to track
    agent usage, token consumption, and performance metrics. Provides
    real-time usage panels and persistent analytics data.
    Usage: Register with container to enable analytics tracking and display
    """

    def services(self):
        return [
            # keep-sorted start
            AgentAnalyticsService,
            # keep-sorted end
        ]
