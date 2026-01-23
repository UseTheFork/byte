from argparse import Namespace

from byte.agent import AgentService, CoderAgent
from byte.cli import ByteArgumentParser, Command
from byte.config import ByteConfigException
from byte.git import GitService
from byte.lint import LintService


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

        try:
            git_service = self.app.make(GitService)
            await git_service.stage_changes()

            lint_service = self.app.make(LintService)
            lint_commands = await lint_service.handle()

            do_fix, failed_commands = await lint_service.display_results_summary(lint_commands)
            if do_fix:
                joined_lint_errors = lint_service.format_lint_errors(failed_commands)
                agent_service = self.app.make(AgentService)
                await agent_service.execute_agent({"errors": joined_lint_errors}, CoderAgent)

        except ByteConfigException as e:
            # log.exception(e)
            console = self.app["console"]
            console.print_error_panel(
                str(e),
                title="Configuration Error",
            )
            return
