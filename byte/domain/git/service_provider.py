from typing import TYPE_CHECKING

from byte.core.service_provider import ServiceProvider
from byte.domain.git.service import GitService

if TYPE_CHECKING:
    from byte.container import Container


class GitServiceProvider(ServiceProvider):
    """Service provider for git repository functionality.

    Registers git service for repository operations, file tracking,
    and integration with other domains that need git context.
    Usage: Register with container to enable git service access
    """

    async def register(self, container: "Container") -> None:
        """Register git services in the container.

        Usage: `provider.register(container)` -> binds git service
        """
        # Register git service
        container.bind("git_service", lambda: GitService(container))

    async def boot(self, container: "Container") -> None:
        """Boot git services.

        Usage: `provider.boot(container)` -> git service becomes available
        """
        pass

    def provides(self) -> list:
        """Return list of services provided by this provider."""
        return ["git_service"]
