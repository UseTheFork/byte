from typing import List, Type

from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.cli.service.command_registry import Command
from byte.domain.git.command.commit_command import CommitCommand
from byte.domain.git.service.git_service import GitService


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
