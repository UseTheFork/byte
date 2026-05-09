from typing import List, Type

from byte import Command, Service, ServiceProvider
from byte.git import (
    CommitAgentNode,
    CommitCommand,
    CommitService,
    CommitWorkflow,
    GitCommitTool,
    GitGrepTool,
    GitLogTool,
    GitService,
)
from byte.node import BaseAgentNode
from byte.tools import BaseTool
from byte.workflow import BaseWorkflow


class GitServiceProvider(ServiceProvider):
    """Service provider for git repository functionality.

    Registers git service for repository operations, file tracking,
    and integration with other domains that need git context.
    Usage: Register with container to enable git service access
    """

    def agents(self) -> List[Type[BaseAgentNode]]:
        return [
            # keep-sorted start
            CommitAgentNode,
            # keep-sorted end
        ]

    def tools(self) -> List[Type[BaseTool]]:
        """Returns the list of git-related tools available to the agent."""
        return [
            # keep-sorted start
            GitCommitTool,
            GitGrepTool,
            GitLogTool,
            # keep-sorted end
        ]

    def services(self) -> List[Type[Service]]:
        return [
            # keep-sorted start
            CommitService,
            GitService,
            # keep-sorted end
        ]

    def commands(self) -> List[Type[Command]]:
        return [
            # keep-sorted start
            CommitCommand,
            # keep-sorted end
        ]

    def workflows(self) -> List[Type[BaseWorkflow]]:
        return [
            # keep-sorted start
            CommitWorkflow,
            # keep-sorted end
        ]
