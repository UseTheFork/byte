from typing import List, Type

from byte.core import Service, ServiceProvider
from byte.domain.cli import Command
from byte.domain.git import CommitCommand, GitService


class GitServiceProvider(ServiceProvider):
    """Service provider for git repository functionality.

    Registers git service for repository operations, file tracking,
    and integration with other domains that need git context.
    Usage: Register with container to enable git service access
    """

    def services(self) -> List[Type[Service]]:
        return [GitService]

    def commands(self) -> List[Type[Command]]:
        return [CommitCommand]
