from argparse import Namespace

from byte import Command
from byte.cli import ByteArgumentParser, InputCancelledError
from byte.git import GitService
from byte.git.service.commit_service import CommitService
from byte.workflow import CommitWorkflow, WorkflowService


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

            commit_workflow = self.app.make(CommitWorkflow)

            workflow_service = self.app.make(WorkflowService)
            commit_result = await workflow_service.execute(commit_workflow, raw_args)

            formatted_message = await self.commit_service.format_conventional_commit(
                commit_result["data"]["result"]["extracted_content"]
            )

            await self.git_service.commit(formatted_message)

        except InputCancelledError:
            return
