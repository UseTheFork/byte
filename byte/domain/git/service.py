from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

from byte.core.config.configurable import Configurable
from byte.core.events.eventable import Eventable
from byte.core.mixins.bootable import Bootable
from byte.domain.git.config import GitConfig

if TYPE_CHECKING:
    pass


class GitService(Bootable, Configurable, Eventable):
    """Domain service for git repository operations and file tracking.

    Provides utilities for discovering changed files, repository status,
    and git operations. Integrates with other domains that need to work
    with modified or staged files in the repository.
    Usage: `changed_files = await git_service.get_changed_files()` -> list of modified files
    """

    async def boot(self) -> None:
        """Initialize git service with configuration.

        Usage: Called automatically during container boot phase
        """
        self._config: Optional[GitConfig] = None
        config_service = await self.container.make("config")
        self._config = config_service.get("git", GitConfig)

    def get_changed_files(
        self, file_extensions: Optional[List[str]] = None
    ) -> List[Path]:
        """Get list of changed files in the repository.

        Args:
            file_extensions: Filter by file extensions (e.g., ['.py', '.js'])

        Returns:
            List of Path objects for changed files

        Usage: `files = git_service.get_changed_files(['.py'])` -> only Python files
        """
        # TODO: Implement git changed files detection
        return []
