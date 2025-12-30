from argparse import Namespace

from byte.core import ByteConfigException, log
from byte.core.utils import list_to_multiline_text
from byte.domain.agent import AgentService, CoderAgent, CommitAgent, CommitPlanAgent
from byte.domain.cli import ByteArgumentParser, Command, ConsoleService
from byte.domain.git import GitService
from byte.domain.lint import LintConfigException, LintService
from byte.domain.prompt_format import Boundary, BoundaryType


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

    async def _format_conventional_commit(self, commit_message) -> str:
        """Format a CommitMessage into a conventional commit string.

        Formats according to the Conventional Commits specification:
        <type>[optional scope][!]: <description>

        [optional body]

        Args:
            commit_message: CommitMessage object to format

        Returns:
            Formatted conventional commit message string

        Usage: `formatted = await self._format_conventional_commit(commit_message)`
        """
        # Build the header line
        header_parts = [commit_message.type]

        if commit_message.scope:
            header_parts.append(f"({commit_message.scope})")

        if commit_message.breaking_change:
            console = await self.make(ConsoleService)

            # Display commit message parts for context
            context_parts = [
                f"Type: {commit_message.type}",
                f"Scope: {commit_message.scope or 'None'}",
                f"Message: {commit_message.commit_message}",
            ]
            if commit_message.body:
                context_parts.append(f"Body: {commit_message.body}")
            if hasattr(commit_message, "files") and commit_message.files:
                context_parts.append(f"Files: {', '.join(commit_message.files)}")

            console.print_panel("\n".join(context_parts), title="Commit Details")

            confirmed = await self.prompt_for_confirmation(
                "This commit is marked as a breaking change. Confirm?", default=True
            )

            if confirmed:
                header_parts.append("!")

        # Normalize the commit message: lowercase first char, remove trailing period
        description = commit_message.commit_message
        description = description[0].lower() + description[1:] if description else description
        description = description.rstrip(".")

        header = "".join(header_parts) + f": {description}"

        # Build the full message
        message_parts = [header]

        if commit_message.body:
            message_parts.extend(["", commit_message.body])

        return "\n".join(message_parts)

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
            formatted_message = await self._format_conventional_commit(commit_group)
            await git_service.commit(formatted_message)

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
            staged_diff = await git_service.get_diff("HEAD")

            # Build formatted diff sections for each file
            diff_section = []
            file_section = [Boundary.open(BoundaryType.CONTEXT, meta={"type": "Files"})]
            for diff_item in staged_diff:
                msg = diff_item["msg"]
                file_path = diff_item["file"]
                change_type = diff_item["change_type"]

                # Start file section with change type
                diff_section.append(
                    Boundary.open(
                        BoundaryType.CONTEXT,
                        meta={"type": "Diff", "change_type": change_type, "file": file_path},
                    )
                )
                file_section.append(f"{msg}")

                # Include diff content only for non-deleted files
                if change_type != "DELETE" and diff_item["diff"]:
                    diff_section.append(diff_item["diff"])

                diff_section.append(Boundary.close(BoundaryType.CONTEXT))

            file_section.append(Boundary.close(BoundaryType.CONTEXT))
            prompt = list_to_multiline_text(diff_section) + list_to_multiline_text(file_section)

            commit_type = await self.prompt_for_select(
                "What type of commit would you like to generate?",
                choices=["Commit Plan", "Single Commit", "Cancel"],
                default="Commit Plan",
            )

            if commit_type == "Commit Plan":
                commit_agent = await self.make(CommitPlanAgent)
                commit_result = await commit_agent.execute(request=prompt, display_mode="thinking")
                log.debug(commit_result)
                await self._process_commit_plan(commit_result["extracted_content"])
            elif commit_type == "Single Commit":
                commit_agent = await self.make(CommitAgent)
                commit_result = await commit_agent.execute(request=prompt, display_mode="thinking")
                formatted_message = await self._format_conventional_commit(commit_result["extracted_content"])
                await git_service.commit(formatted_message)
        except ByteConfigException as e:
            console = await self.make(ConsoleService)
            console.print_error_panel(
                str(e),
                title="Configuration Error",
            )
            return
