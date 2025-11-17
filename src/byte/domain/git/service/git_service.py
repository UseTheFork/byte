from pathlib import Path
from typing import List

import git
from git.exc import InvalidGitRepositoryError

from byte.core.mixins.user_interactive import UserInteractive
from byte.core.service.base_service import Service
from byte.domain.cli.service.console_service import ConsoleService


class GitService(Service, UserInteractive):
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

    async def commit(self, commit_message: str) -> None:
        """Create a git commit with the provided message.

        Args:
                commit_message: The commit message to use

        Usage: `await git_service.commit("feat: add new feature")` -> creates commit with message
        """
        console = await self.make(ConsoleService)

        continue_commit = True

        while continue_commit:
            try:
                # Create the commit
                commit = self._repo.index.commit(commit_message)
                commit_hash = commit.hexsha[:6]

                # Display success panel
                console.print_success_panel(
                    f"({commit_hash}) {commit_message}",
                    title="Commit Created",
                )

                # Exit loop on successful commit
                continue_commit = False

            except Exception as e:
                # Display error panel if commit fails
                console.print_error_panel(f"Failed to create commit: {e!s}", title="Commit Failed")

                # Prompt user to retry with staging
                retry = await self.prompt_for_confirmation("Stage changes and try again?", default=True)

                if retry:
                    # Stage changes and retry commit
                    await self.stage_changes()
                    # Loop continues for another attempt
                else:
                    # User declined retry, exit loop
                    continue_commit = False

    async def stage_changes(self) -> None:
        """Check for unstaged changes and offer to add them to the commit.

        Args:
                repo: Git repository instance
                console: Rich console for output

        Usage: Called internally during commit process to handle unstaged files
        """
        console = await self.make(ConsoleService)
        unstaged_changes = self._repo.index.diff(None)  # None compares working tree to index
        if unstaged_changes:
            file_list = []
            for change in unstaged_changes:
                change_type = (
                    "modified" if change.change_type == "M" else "new" if change.change_type == "A" else "deleted"
                )
                file_list.append(f"  • {change.a_path} ({change_type})")

            files_display = "\n".join(file_list)

            console.print_panel(
                f"Found {len(unstaged_changes)} unstaged changes:\n\n{files_display}",
                title="[warning]Unstaged Changes[/warning]",
                border_style="warning",
            )

            user_input = await self.prompt_for_confirmation("Add unstaged changes to commit?", True)

            if user_input:
                # Add all unstaged changes
                self._repo.git.add("--all")
                console.print_success(f"Added {len(unstaged_changes)} unstaged changes to commit")
