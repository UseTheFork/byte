from argparse import Namespace

from byte import ByteArgumentParser, Command
from byte.coder import CoderWorkflow
from byte.config import ByteConfigException
from byte.git import GitService
from byte.lint import LintService
from byte.orchestration import WorkflowService
from byte.tui import Messages


class LintCommand(Command):
    """Command to run code linting on changed files or current context.

    Executes configured lint commands on files to identify and fix code
    quality issues. Can target git changed files or files in AI context.
    Usage: `/lint` -> runs linters on changed files, `/lint context` -> runs on AI context
    """

    @property
    def name(self) -> str:
        return "lint"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Run configured linters on changed files or current context",
        )
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Execute linting command with optional arguments."""

        self.emit_tui(Messages.CommandExecutionStarted())

        try:
            git_service = self.app.make(GitService)
            await git_service.stage_changes()

            lint_service = self.app.make(LintService)
            lint_commands = await lint_service.handle()

            do_fix, failed_commands = await lint_service.display_results_summary(lint_commands)
            if do_fix:
                joined_lint_errors = lint_service.format_lint_errors(failed_commands)

                coder_workflow = self.app.make(CoderWorkflow)
                workflow_service = self.app.make(WorkflowService)
                await workflow_service.execute(coder_workflow, {"user_request": joined_lint_errors})

        except ByteConfigException as e:
            await self.notify_error(str(e))

        self.emit_tui(Messages.CommandExecutionCompleted())
