from byte.core.exceptions import ByteConfigException
from byte.domain.cli.service.command_registry import Command
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.git.service.git_service import GitService
from byte.domain.lint.service.lint_service import LintService


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
			args: Command arguments - 'context' for AI context files, or file extensions like 'py js' for specific types

		Usage: Called by command processor when user types `/lint [args]`
		"""

		try:
			git_service = await self.make(GitService)
			await git_service.stage_changes()

			lint_service = await self.make(LintService)
			await lint_service()
		except ByteConfigException as e:
			console = await self.make(ConsoleService)
			console.print_error_panel(
				str(e),
				title="Configuration Error",
			)
			return
