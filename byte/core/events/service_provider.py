from byte.container import Container
from byte.core.service_provider import ServiceProvider

from .dispatcher import EventDispatcher


class EventServiceProvider(ServiceProvider):
    """Service provider for event system."""

    def register(self, container: Container):
        """Register event services in the container."""
        container.singleton("event_dispatcher", lambda: EventDispatcher())

    def boot(self, container: Container):
        """Boot event services."""
        # Event listeners will be registered by domain service providers
        pass

    def provides(self) -> list:
        return ["event_dispatcher"]
