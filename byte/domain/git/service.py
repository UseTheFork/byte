from pathlib import Path
from typing import TYPE_CHECKING, List

import git
from git.exc import InvalidGitRepositoryError

from byte.core.config.mixins import Configurable
from byte.core.service.mixins import Bootable
from byte.domain.events.mixins import Eventable

if TYPE_CHECKING:
    pass


class GitService(Bootable, Configurable, Eventable):
    """Domain service for git repository operations and file tracking.

    Provides utilities for discovering changed files, repository status,
    and git operations. Integrates with other domains that need to work
    with modified or staged files in the repository.
    Usage: `changed_files = await git_service.get_changed_files()` -> list of modified files
    """

    async def boot(self):
        # Initialize git repository using the project root from config
        try:
            self._repo = git.Repo(self._config.project_root)
        except InvalidGitRepositoryError:
            raise InvalidGitRepositoryError(
                f"Not a git repository: {self._config.project_root}. Please run 'git init' or navigate to a git repository."
            )

    async def get_repo(self):
        """Get the git repository instance, ensuring service is booted.

        Usage: `repo = await git_service.get_repo()` -> git.Repo instance
        """
        await self.ensure_booted()
        return self._repo

    async def get_changed_files(self, include_untracked: bool = True) -> List[Path]:
        """Get list of changed files in the repository.

        Args:
            include_untracked: Include untracked files in the results

        Returns:
            List of Path objects for changed files

        Usage: `files = git_service.get_changed_files()` -> all changed files including untracked
        """
        if not self._repo:
            return []

        changed_files = []

        # Get modified and staged files
        for item in self._repo.index.diff(None):  # Working tree vs index
            changed_files.append(Path(item.a_path))

        for item in self._repo.index.diff("HEAD"):  # Index vs HEAD
            changed_files.append(Path(item.a_path))

        # Get untracked files if requested
        if include_untracked:
            for untracked_file in self._repo.untracked_files:
                changed_files.append(Path(untracked_file))

        # Remove duplicates and return
        return list(set(changed_files))
