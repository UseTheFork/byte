from byte.container import Container
from byte.core.service_provider import ServiceProvider
from byte.domain.events.dispatcher import EventDispatcher


class EventServiceProvider(ServiceProvider):
    """Service provider for the event system infrastructure.

    Registers the event dispatcher as a singleton to ensure all services
    share the same event bus for proper cross-domain communication.
    """

    async def register(self, container: Container):
        """Register event dispatcher as singleton for shared event bus."""
        # Singleton ensures all services use the same dispatcher instance
        container.singleton(EventDispatcher)

    async def boot(self, container: Container):
        """Boot event services after all providers are registered.

        Domain service providers will register their specific event listeners
        during their own boot phase to ensure proper dependency resolution.
        """
        # Event listeners will be registered by domain service providers
        pass

    def provides(self) -> list:
        return [EventDispatcher]
