from rich.console import Console

from byte.domain.agent.commit.agent import CommitAgent
from byte.domain.cli_input.service.command_registry import Command
from byte.domain.git.service.git_service import GitService
from byte.domain.lint.service.lint_service import LintService


class CommitCommand(Command):
    """Command to create AI-powered git commits with automatic staging and linting.

    Stages all changes, runs configured linters, generates an intelligent commit
    message using AI analysis of the staged diff, and handles the complete
    commit workflow with user interaction.
    Usage: `/commit` -> stages changes, lints, generates commit message
    """

    @property
    def name(self) -> str:
        return "commit"

    @property
    def description(self) -> str:
        return "Create an AI-powered git commit with automatic staging and linting"

    async def execute(self, args: str) -> None:
        """Execute the commit command with full workflow automation.

        Stages all changes, validates that changes exist, runs linting on
        changed files, generates an AI commit message from the staged diff,
        and returns control to user input after completion.

        Args:
            args: Command arguments (currently unused)

        Usage: Called automatically when user types `/commit`
        """
        console = await self.make(Console)
        git_service = await self.make(GitService)
        await git_service.stage_changes()

        repo = await git_service.get_repo()

        # Validate staged changes exist to prevent empty commits
        if not repo.index.diff("HEAD"):
            console.print("[warning]No staged changes to commit.[/warning]")
            await self.prompt_for_input()
            return

        lint_service = await self.make(LintService)
        await lint_service.lint_changed_files()

        # Extract staged changes for AI analysis
        staged_diff = repo.git.diff("--cached")

        commit_agent = await self.make(CommitAgent)
        commit_message = await commit_agent.execute(staged_diff)

        await git_service.commit(commit_message)

        await self.prompt_for_input()
