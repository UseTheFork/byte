from typing import TYPE_CHECKING

from byte.core.config.service import ConfigService
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
        # Register memory service
        container.singleton("memory_service", lambda: MemoryService(container))

    async def configure(self, container: "Container") -> None:
        """Configure lint domain settings after registration but before boot.

        Handles lint-specific configuration parsing, validation, and storage.
        Usage: Called automatically during container configure phase
        """
        # Get the config service to access raw configuration data
        config_service: ConfigService = await container.make("config")

        # Get raw config data from all sources
        yaml_config, env_config, cli_config = config_service.get_raw_config()

        config = MemoryConfig(database_path=config_service.byte_dir / "memory.db")

        memory_service: MemoryService = await container.make("memory_service")
        memory_service.set_config(config)

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
