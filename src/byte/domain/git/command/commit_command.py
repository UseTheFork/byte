from byte.core.exceptions import ByteConfigException
from byte.domain.agent.implementations.commit.agent import CommitAgent
from byte.domain.cli.service.command_registry import Command
from byte.domain.cli.service.console_service import ConsoleService
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
		try:
			console = await self.make(ConsoleService)
			git_service = await self.make(GitService)
			await git_service.stage_changes()

			repo = await git_service.get_repo()

			# Validate staged changes exist to prevent empty commits
			if not repo.index.diff("HEAD"):
				console.print_warning("No staged changes to commit.")
				return

			lint_service = await self.make(LintService)
			await lint_service()

			# Extract staged changes for AI analysis
			staged_diff = repo.git.diff("--cached")

			commit_agent = await self.make(CommitAgent)
			commit_message: dict = await commit_agent.execute(
				request={"messages": [("user", staged_diff)]}, display_mode="thinking"
			)

			await git_service.commit(str(commit_message.get("extracted_content", "")))
		except ByteConfigException as e:
			console = await self.make(ConsoleService)
			console.print_error_panel(
				str(e),
				title="Configuration Error",
			)
			return
