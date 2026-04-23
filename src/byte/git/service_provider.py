from typing import List, Type

from langchain.tools import BaseTool

from byte import Command, Service, ServiceProvider
from byte.git import CommitCommand, CommitService, GitCommitTool, GitGrepTool, GitService


class GitServiceProvider(ServiceProvider):
    """Service provider for git repository functionality.

    Registers git service for repository operations, file tracking,
    and integration with other domains that need git context.
    Usage: Register with container to enable git service access
    """

    def tools(self) -> List[Type[BaseTool]]:
        """"""
        return [
            GitGrepTool,
            GitCommitTool,
        ]

    def services(self) -> List[Type[Service]]:
        return [
            GitService,
            CommitService,
        ]

    def commands(self) -> List[Type[Command]]:
        return [CommitCommand]
