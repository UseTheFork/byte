from typing import TYPE_CHECKING

from byte.context import make
from byte.core.command.registry import Command
from byte.domain.lint.service import LintService

if TYPE_CHECKING:
    from rich.console import Console


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
    def description(self) -> str:
        return "Run configured linters on changed files or current context"

    async def execute(self, args: str) -> None:
        """Execute linting command with optional arguments.

        Args:
            args: Command arguments - 'context' for AI context files,
                  or file extensions like 'py js' for specific types

        Usage: Called by command processor when user types `/lint [args]`
        """
        console: Console = await make("console")
        lint_service: LintService = await make("lint_service")
        await lint_service.lint_changed_files()

        # TODO: Implement lint command execution
        console.print("[info]Lint command not yet implemented[/info]")
