from rich.console import Console

from byte.core.logging import log
from byte.domain.agent.commit.agent import CommitAgent
from byte.domain.cli_input.service.command_registry import Command
from byte.domain.git.service.git_service import GitService
from byte.domain.lint.service.lint_service import LintService


class CommitCommand(Command):
    """Foo"""

    @property
    def name(self) -> str:
        return "commit"

    @property
    def description(self) -> str:
        return "Bar"

    async def execute(self, args: str) -> None:
        """Foo"""
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
        message = await commit_agent.execute(staged_diff)
        log.info(message)

        await self.prompt_for_input()
