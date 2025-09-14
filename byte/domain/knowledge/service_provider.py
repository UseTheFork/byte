from typing import TYPE_CHECKING

from byte.core.service_provider import ServiceProvider
from byte.domain.knowledge.config import KnowledgeConfig
from byte.domain.knowledge.service import KnowledgeService

if TYPE_CHECKING:
    from byte.container import Container


class KnowledgeServiceProvider(ServiceProvider):
    """Service provider for long-term knowledge management.

    Registers knowledge services for persistent storage of user preferences,
    project patterns, and learned behaviors. Enables cross-session memory
    and intelligent context building for the AI agent system.
    Usage: Register with container to enable long-term knowledge storage
    """

    async def register(self, container: "Container") -> None:
        """Register knowledge services in the container.

        Usage: `provider.register(container)` -> binds knowledge services
        """
        # Register knowledge config schema
        config_service = await container.make("config")
        config_service.register_schema("knowledge", KnowledgeConfig)

        # Register knowledge service
        container.singleton("knowledge_service", lambda: KnowledgeService(container))

    async def boot(self, container: "Container") -> None:
        """Boot knowledge services after all providers are registered.

        Usage: `provider.boot(container)` -> knowledge system ready for use
        """
        # Knowledge service is lazy-loaded, no explicit boot needed
        pass

    async def shutdown(self, container: "Container"):
        """Shutdown knowledge services and close database connections."""
        try:
            if "knowledge_service" in container._instances:
                knowledge_service = await container.make("knowledge_service")
                await knowledge_service.close()
        except Exception:
            pass  # Ignore cleanup errors during shutdown

    def provides(self) -> list:
        """Return list of services provided by this provider."""
        return ["knowledge_service"]
