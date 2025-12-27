from argparse import Namespace

from byte.core import log
from byte.core.exceptions import ByteConfigException
from byte.core.utils.list_to_multiline_text import list_to_multiline_text
from byte.domain.agent.implementations.coder.agent import CoderAgent
from byte.domain.agent.implementations.commit.agent import CommitAgent, CommitPlanAgent
from byte.domain.agent.service.agent_service import AgentService
from byte.domain.cli.argparse.base import ByteArgumentParser
from byte.domain.cli.service.command_registry import Command
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.git.service.git_service import GitService
from byte.domain.lint.exceptions import LintConfigException
from byte.domain.lint.service.lint_service import LintService
from byte.domain.prompt_format.schemas import BoundaryType
from byte.domain.prompt_format.utils import Boundary


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

    async def _process_commit_plan(self, commit_plan) -> None:
        """Process the commit plan by unstaging all files and committing each group separately.

        Unstages all currently staged files, then iterates through each commit group
        in the plan, staging only the files for that group and creating a commit with
        the group's message.

        Args:
            commit_plan: The CommitPlan containing commit groups with messages and files

        Usage: `await self._process_commit_plan(commit_plan)`
        """
        git_service = await self.make(GitService)

        # Unstage all files
        await git_service.reset()

        # Iterate over each commit group
        log.debug(commit_plan)
        for commit_group in commit_plan.commits:
            # Stage files for this commit group
            for file_path in commit_group.files:
                file_full_path = self._config.project_root / file_path
                if file_full_path.exists():
                    await git_service.add(file_path)
                else:
                    # File was deleted, stage the deletion
                    await git_service.remove(file_path)

            # Commit with the group's message
            await git_service.commit(commit_group.commit_message)

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
                    await agent_service.execute_agent(joined_lint_errors, CoderAgent)
            except LintConfigException:
                pass

            # Extract staged changes for AI analysis
            staged_diff = repo.git.diff("--cached")

            # Get list of staged file paths
            staged_files = [item.a_path for item in repo.index.diff("HEAD")]

            # TODO: need to implment `count_tokens_approximately`
            # tokens = count_tokens_approximately([("user", staged_diff)])

            # Combine diff and file list for AI analysis
            staged_files_list = "\n".join(f"- {file}" for file in staged_files)
            prompt = list_to_multiline_text(
                [
                    Boundary.open(BoundaryType.CONTEXT, meta={"type": "Staged Files"}),
                    staged_files_list,
                    Boundary.close(BoundaryType.CONTEXT),
                    "",
                    Boundary.open(BoundaryType.CONTEXT, meta={"type": "Diff"}),
                    staged_diff,
                    Boundary.close(BoundaryType.CONTEXT),
                ]
            )

            commit_type = await self.prompt_for_select(
                "What type of commit would you like to generate?",
                choices=["Commit Plan", "Single Commit", "Cancel"],
                default="Commit Plan",
            )

            if commit_type == "Commit Plan":
                commit_agent = await self.make(CommitPlanAgent)
                commit_result = await commit_agent.execute(request=prompt, display_mode="thinking")
                await self._process_commit_plan(commit_result["extracted_content"])
            elif commit_type == "Single Commit":
                commit_agent = await self.make(CommitAgent)
                commit_result = await commit_agent.execute(request=prompt, display_mode="thinking")
                commit_message = commit_result["extracted_content"].commit_message
                await git_service.commit(commit_message)
        except ByteConfigException as e:
            console = await self.make(ConsoleService)
            console.print_error_panel(
                str(e),
                title="Configuration Error",
            )
            return
