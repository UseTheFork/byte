from typing import List, Type

from byte.core import Service, ServiceProvider
from byte.domain.git import GitService


class GitServiceProvider(ServiceProvider):
    """Service provider for git repository functionality.

    Registers git service for repository operations, file tracking,
    and integration with other domains that need git context.
    Usage: Register with container to enable git service access
    """

    def services(self) -> List[Type[Service]]:
        return [GitService]
