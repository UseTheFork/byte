from typing import TYPE_CHECKING

from byte.core.service_provider import ServiceProvider

if TYPE_CHECKING:
    from byte.container import Container


class ToolsServiceProvider(ServiceProvider):
    """Service provider for agent tools and utilities.

    Registers reusable tools that can be shared across different agents,
    including file operations, git utilities, and system commands. Promotes
    code reuse and consistent tool behavior across the agent ecosystem.
    Usage: Automatically registered during bootstrap to make tools available
    """

    async def register(self, container: "Container") -> None:
        """Register tool services in the container.

        Usage: `provider.register(container)` -> binds tool services
        """
        # Tools are stateless functions, no services to register yet
        pass

    async def boot(self, container: "Container") -> None:
        """Boot tool services after all providers are registered.

        Usage: `provider.boot(container)` -> tools ready for agent use
        """
        # Tools are ready to use after import, no boot process needed
        pass

    def provides(self) -> list:
        """Return list of services provided by this provider."""
        return []
