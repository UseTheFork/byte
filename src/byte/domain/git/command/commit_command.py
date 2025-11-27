from argparse import Namespace

from byte.core.exceptions import ByteConfigException
from byte.domain.agent.implementations.coder.agent import CoderAgent
from byte.domain.agent.implementations.commit.agent import CommitAgent
from byte.domain.agent.service.agent_service import AgentService
from byte.domain.cli.argparse.base import ByteArgumentParser
from byte.domain.cli.service.command_registry import Command
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.git.service.git_service import GitService
from byte.domain.lint.exceptions import LintConfigException
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
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Create an AI-powered git commit with automatic staging and linting",
        )
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Execute the commit command with full workflow automation.

        Stages all changes, validates that changes exist, runs linting on
        changed files, generates an AI commit message from the staged diff,
        and returns control to user input after completion.

        Args:
                args: Command arguments (currently unused)

        Usage: Called automatically when user types `/commit`
        """
        try:
            console = await self.make(ConsoleService)
            git_service = await self.make(GitService)
            await git_service.stage_changes()

            repo = await git_service.get_repo()

            # Validate staged changes exist to prevent empty commits
            if not repo.index.diff("HEAD"):
                console.print_warning("No staged changes to commit.")
                return

            try:
                lint_service = await self.make(LintService)
                lint_commands = await lint_service()

                do_fix, failed_commands = await lint_service.display_results_summary(lint_commands)
                if do_fix:
                    joined_lint_errors = lint_service.format_lint_errors(failed_commands)
                    agent_service = await self.make(AgentService)
                    await agent_service.execute_agent({"errors": joined_lint_errors}, CoderAgent)
            except LintConfigException:
                pass

            # Extract staged changes for AI analysis
            staged_diff = repo.git.diff("--cached")

            # TODO: need to implment `count_tokens_approximately`
            # tokens = count_tokens_approximately([("user", staged_diff)])

            commit_agent = await self.make(CommitAgent)
            commit_message = await commit_agent.execute(request=staged_diff, display_mode="thinking")

            await git_service.commit(str(commit_message["extracted_content"]))
        except ByteConfigException as e:
            console = await self.make(ConsoleService)
            console.print_error_panel(
                str(e),
                title="Configuration Error",
            )
            return
