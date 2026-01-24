from argparse import Namespace

from byte.agent import AgentService, CoderAgent, CommitAgent, CommitPlanAgent
from byte.cli import ByteArgumentParser, Command, InputCancelledError
from byte.git import GitService
from byte.git.service.commit_service import CommitService
from byte.lint import LintConfigException, LintService


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

    def boot(self, *args, **kwargs) -> None:
        self.commit_service = self.app.make(CommitService)
        self.git_service = self.app.make(GitService)

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
            console = self.app["console"]
            await self.git_service.stage_changes()

            # Validate staged changes exist to prevent empty commits

            diff = await self.git_service.get_diff()
            if not diff:
                console.print_warning("No staged changes to commit.")
                return

            try:
                lint_service = self.app.make(LintService)
                lint_commands = await lint_service()

                do_fix, failed_commands = await lint_service.display_results_summary(lint_commands)
                if do_fix:
                    joined_lint_errors = lint_service.format_lint_errors(failed_commands)
                    agent_service = self.app.make(AgentService)
                    await agent_service.execute_agent(joined_lint_errors, CoderAgent)
            except LintConfigException:
                pass

            # Stage the changes again if anything changed via the lint.
            await self.git_service.stage_changes()

            prompt = await self.commit_service.build_commit_prompt()

            commit_type = await self.prompt_for_select(
                "What type of commit would you like to generate?",
                choices=["Commit Plan", "Single Commit", "Cancel"],
                default="Commit Plan",
            )

            if commit_type == "Commit Plan":
                commit_agent = self.app.make(CommitPlanAgent)
                commit_result = await commit_agent.execute(request=prompt, display_mode="thinking")
                await self.commit_service.process_commit_plan(commit_result["extracted_content"])
            elif commit_type == "Single Commit":
                commit_agent = self.app.make(CommitAgent)
                commit_result = await commit_agent.execute(request=prompt, display_mode="thinking")
                formatted_message = await self.commit_service.format_conventional_commit(
                    commit_result["extracted_content"]
                )
                await self.git_service.commit(formatted_message)

        except InputCancelledError:
            return
