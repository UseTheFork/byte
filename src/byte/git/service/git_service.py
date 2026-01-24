from difflib import unified_diff
from pathlib import Path
from typing import List

import git
from git.exc import InvalidGitRepositoryError

from byte import Service
from byte.support.mixins import UserInteractive


class GitService(Service, UserInteractive):
    """Domain service for git repository operations and file tracking.

    Provides utilities for discovering changed files, repository status,
    and git operations. Integrates with other domains that need to work
    with modified or staged files in the repository.
    Usage: `changed_files = await git_service.get_changed_files()` -> list of modified files
    """

    def boot(self):
        # Initialize git repository using the project root from config
        try:
            self._repo = git.Repo(self.app["path.root"])
        except InvalidGitRepositoryError:
            raise InvalidGitRepositoryError(
                f"Not a git repository: {self.app['path.root']}. Please run 'git init' or navigate to a git repository."
            )

    async def get_repo(self):
        """Get the git repository instance, ensuring service is booted.

        Usage: `repo = await git_service.get_repo()` -> git.Repo instance
        """
        self.ensure_booted()
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
        console = self.app["console"]

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
                        file_full_path = self.app.root_path(str(file_path))
                        if file_full_path.exists():
                            await self.add(str(file_path))
                        else:
                            # File was deleted, stage the deletion
                            await self.remove(str(file_path))
                    # Loop continues for another attempt
                else:
                    # User declined retry, exit loop
                    continue_commit = False

    async def stage_changes(self, force: bool = False) -> None:
        """Check for unstaged changes and offer to add them to the commit.

        Args:
                repo: Git repository instance
                console: Rich console for output

        Usage: Called internally during commit process to handle unstaged files
        """
        console = self.app["console"]
        unstaged_changes = self._repo.index.diff(None)  # None compares working tree to index
        untracked_files = self._repo.untracked_files

        if unstaged_changes or untracked_files:
            file_list = []
            for change in unstaged_changes:
                change_type = (
                    "modified" if change.change_type == "M" else "new" if change.change_type == "A" else "deleted"
                )
                file_list.append(f"  • {change.a_path} ({change_type})")

            for untracked in untracked_files:  # Add this loop
                file_list.append(f"  • {untracked} (new)")

            files_display = "\n".join(file_list)

            total_changes = len(unstaged_changes) + len(untracked_files)

            console.print_panel(
                f"Found {len(unstaged_changes)} unstaged changes and {len(untracked_files)} untracked changes:\n\n{files_display}",
                title="[warning]Unstaged Changes[/warning]",
                border_style="warning",
            )

            if not force:
                user_input = await self.prompt_for_confirmation("Add unstaged and untracked changes to commit?", True)
            else:
                user_input = True

            if user_input:
                # Add all unstaged changes
                self._repo.git.add("--all")
                console.print_success(f"Added {total_changes} changes to commit")

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

    async def get_diff(self) -> List[dict]:
        """Get structured diff data for changes in the repository.

        Returns:
                List of dictionaries containing diff information for each changed file

        Usage: `await git_service.get_diff()` -> get staged changes
        """

        staged_diff = self._repo.head.commit.diff()

        diff_data = []
        for diff_item in staged_diff:
            diff_content = ""

            change_type = diff_item.change_type

            self.app["log"].info(f"change_type: {diff_item.change_type}")

            match diff_item.change_type:
                case "A":
                    msg = f"new: {diff_item.a_path}"
                case "D":
                    msg = f"deleted: {diff_item.a_path}"
                case "M":
                    msg = f"modified: {diff_item.a_path}"
                case "R":
                    msg = f"renamed: {diff_item.a_path} -> {diff_item.b_path}"
                case _:
                    msg = f"type {diff_item.change_type}: {diff_item.a_path}"

            if diff_item.a_blob and change_type == "M":
                try:
                    head_data = diff_item.a_blob.data_stream.read()
                    # Check if binary (contains null bytes)
                    if b"\0" not in head_data:
                        # Text file - generate diff
                        staged_entry = self._repo.index.entries.get((diff_item.a_path, 0))
                        if staged_entry:
                            staged_data = self._repo.odb.stream(staged_entry.binsha).read().decode("utf-8")
                            head_data_str = head_data.decode("utf-8")

                            for line in unified_diff(
                                head_data_str.splitlines(),
                                staged_data.splitlines(),
                                lineterm="",
                            ):
                                diff_content += line + "\n"
                    else:
                        # Binary file - don't include diff content
                        diff_content = None
                except UnicodeDecodeError:
                    # Binary file
                    diff_content = None

            # Clear diff content for deletions since the file no longer exists
            if change_type == "D":
                diff_content = None

            diff_data.append(
                {
                    "file": diff_item.a_path,
                    "change_type": diff_item.change_type,
                    "diff": diff_content,
                    "msg": msg,
                    "is_renamed": change_type == "R",
                    "is_modified": change_type == "M",
                    "is_new": change_type == "A",
                    "is_deleted": change_type == "D",
                }
            )

        return diff_data
