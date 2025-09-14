from typing import TYPE_CHECKING

from byte.core.service_provider import ServiceProvider
from byte.domain.memory.config import MemoryConfig
from byte.domain.memory.service import MemoryService

if TYPE_CHECKING:
    from byte.container import Container


class MemoryServiceProvider(ServiceProvider):
    """Service provider for conversation memory management.

    Registers memory services for short-term conversation persistence using
    LangGraph checkpointers. Enables stateful conversations and thread
    management for the AI agent system.
    Usage: Register with container to enable conversation memory
    """

    async def register(self, container: "Container") -> None:
        """Register memory services in the container.

        Usage: `provider.register(container)` -> binds memory services
        """
        # Register memory config schema
        config_service = await container.make("config")
        config_service.register_schema("memory", MemoryConfig)

        # Register memory service
        container.singleton("memory_service", lambda: MemoryService(container))

    async def boot(self, container: "Container") -> None:
        """Boot memory services after all providers are registered.

        Usage: `provider.boot(container)` -> memory system ready for use
        """
        # Memory service is lazy-loaded, no explicit boot needed
        pass

    async def shutdown(self, container: "Container"):
        """Shutdown memory services and close database connections."""
        try:
            if "memory_service" in container._instances:
                memory_service = await container.make("memory_service")
                await memory_service.close()
        except Exception:
            pass  # Ignore cleanup errors during shutdown

    def provides(self) -> list:
        """Return list of services provided by this provider."""
        return ["memory_service"]
