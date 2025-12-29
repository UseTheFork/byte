from pathlib import Path
from typing import List

import git
from git.exc import InvalidGitRepositoryError

from byte import Service
from byte.core.mixins import UserInteractive
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
            changed_files.append(Path(str(item.a_path)))

        for item in self._repo.index.diff("HEAD"):  # Index vs HEAD
            changed_files.append(Path(str(item.a_path)))

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

        # Record currently staged files before attempting commit
        staged_files = [item.a_path for item in self._repo.index.diff("HEAD")]

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
                    # Re-stage only the files that were originally staged for this commit
                    for file_path in staged_files:
                        file_full_path = self._config.project_root / file_path
                        if file_full_path.exists():
                            await self.add(str(file_path))
                        else:
                            # File was deleted, stage the deletion
                            await self.remove(str(file_path))
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

    async def reset(self, file_path: str | None = None) -> None:
        """Unstage files from the git index.

        Args:
                file_path: Optional path to specific file to unstage. If None, unstages all files.

        Usage: `await git_service.reset("config.py")` -> unstages specific file
        Usage: `await git_service.reset()` -> unstages all files
        """
        if file_path:
            self._repo.index.reset(paths=[file_path])
        else:
            self._repo.index.reset()

    async def add(self, file_path: str) -> None:
        """Stage a specific file to the git index.

        Args:
                file_path: Path to the file to stage

        Usage: `await git_service.add("config.py")` -> stages specific file
        """
        self._repo.index.add([file_path])

    async def remove(self, file_path: str) -> None:
        """Stage a file deletion to the git index.

        Args:
                file_path: Path to the deleted file to stage

        Usage: `await git_service.remove("config.py")` -> stages file deletion
        """
        self._repo.index.remove([file_path])

    async def get_diff(self, other: str | None = None) -> List[dict]:
        """Get structured diff data for changes in the repository.

        Args:
                other: Optional comparison target. Common values:
                        - None: Compare working tree to index (unstaged changes)
                        - "HEAD": Compare index to HEAD (staged changes)
                        - "--cached": Same as "HEAD" (staged changes)

        Returns:
                List of dictionaries containing diff information for each changed file

        Usage: `await git_service.get_diff("HEAD")` -> get staged changes
        Usage: `await git_service.get_diff()` -> get unstaged changes
        """

        staged_diff = self._repo.index.diff(other, create_patch=True)

        diff_data = []
        for diff_item in staged_diff:
            diff_content = None

            # Determine change type by checking blob existence
            if diff_item.a_blob is not None and diff_item.b_blob is None:
                # No old blob, has new blob = file was added
                change_type = "ADD"
            elif diff_item.a_blob is None and diff_item.b_blob is not None:
                # Has old blob, no new blob = file was deleted
                change_type = "DELETE"
            elif diff_item.renamed:
                change_type = "RENAME FILE"
            else:
                # Both blobs exist = file was modified
                change_type = "MODIFY"

            if diff_item.diff:
                if isinstance(diff_item.diff, bytes):
                    diff_content = diff_item.diff.decode("utf-8")
                else:
                    diff_content = str(diff_item.diff)

            # Clear diff content for deletions since the file no longer exists
            if change_type == "DELETE":
                diff_content = None

            diff_data.append(
                {
                    "file": diff_item.a_path,
                    "change_type": change_type,
                    "diff": diff_content,
                    "renamed": diff_item.renamed,
                    "new_file": change_type == "ADD",
                    "deleted_file": change_type == "DELETE",
                }
            )

        return diff_data
