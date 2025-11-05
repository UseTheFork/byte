import asyncio
from pathlib import Path
from typing import List

from rich.console import Group
from rich.live import Live
from rich.progress import BarColumn, Progress, TaskProgressColumn
from rich.table import Column

from byte.core.logging import log
from byte.core.mixins.user_interactive import UserInteractive
from byte.core.service.base_service import Service
from byte.core.utils import get_language_from_filename
from byte.core.utils.list_to_multiline_text import list_to_multiline_text
from byte.domain.cli.rich.markdown import Markdown
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.git.service.git_service import GitService
from byte.domain.lint.exceptions import LintConfigException
from byte.domain.lint.types import LintCommand, LintFile
from byte.domain.prompt_format.schemas import BoundaryType
from byte.domain.prompt_format.utils.boundary import Boundary


class LintService(Service, UserInteractive):
    """Domain service for code linting and formatting operations.

    Orchestrates multiple linting commands configured in config.yaml to analyze
    and optionally fix code quality issues. Integrates with git service to
    target only changed files for efficient linting workflows.
    Usage: `await lint_service.lint_changed_files()` -> runs configured linters on git changes
    """

    async def validate(self) -> bool:
        """Validate lint service configuration before execution.

        Checks that linting is enabled and at least one lint command is configured.
        Raises LintConfigException if configuration is invalid.

        Returns:
                True if validation passes.

        Raises:
                LintConfigException: If linting is disabled or no commands configured.

        Usage: `await service.validate()` -> ensure lint config is valid
        """
        if not self._config.lint.enable:
            raise LintConfigException(
                "Linting is disabled. Set 'lint.enable' to true in your .byte/config.yaml to use lint commands."
            )

        if len(self._config.lint.commands) == 0:
            raise LintConfigException(
                "No lint commands configured. Add commands to 'lint.commands' in your .byte/config.yaml. "
                "See docs/reference/settings.md for configuration examples."
            )

        return True

    async def handle(self, **kwargs):
        """Handle lint service execution - main entry point for linting operations."""

        return await self.lint_changed_files()

    async def lint_changed_files(self) -> List[LintCommand]:
        """Run configured linters on git changed files.

        Returns:
                List of LintCommand objects with results

        Usage: `results = await lint_service.lint_changed_files()` -> lint changed files
        """

        git_service: GitService = await self.make(GitService)
        all_changed_files = await git_service.get_changed_files()

        # Filter out removed files - only lint files that actually exist
        changed_files = [f for f in all_changed_files if f.exists()]

        return await self.lint_files(changed_files)

    async def _execute_lint_command(self, lint_file: LintFile, git_root) -> LintFile:
        try:
            # Run the command and capture output
            process = await asyncio.create_subprocess_shell(
                lint_file.full_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=git_root,
            )

            stdout, stderr = await process.communicate()
            exit_code = process.returncode

            # Return updated LintFile with results
            return LintFile(
                file=lint_file.file,
                full_command=lint_file.full_command,
                exit_code=exit_code,
                stdout=stdout.decode("utf-8", errors="ignore"),
                stderr=stderr.decode("utf-8", errors="ignore"),
            )

        except Exception as e:
            # Handle command execution errors
            return LintFile(
                file=lint_file.file,
                full_command=lint_file.full_command,
                exit_code=-1,
                stdout="",
                stderr=f"Error executing command: {e!s}",
            )

    async def display_results_summary(self, lint_commands: List[LintCommand]) -> tuple[bool, list]:
        """Display a summary panel of linting results.

        Args:
                lint_commands: List of LintCommand objects with results
        """

        if not lint_commands:
            return (False, [])

        # Count total files processed and issues found
        total_files = 0
        total_issues = 0
        commands_with_issues = []
        failed_commands = []

        for command in lint_commands:
            total_files += len(command.results)

            # Get files with issues for this command
            failed_files = [lint_file for lint_file in command.results if lint_file.exit_code != 0]

            if failed_files:
                total_issues += len(failed_files)

                # Append failed files to failed_commands list
                failed_commands.extend(failed_files)

                # Add command header
                command_str = " ".join(command.command)
                commands_with_issues.append(f"# **{command_str}** ({len(failed_files)} files)\n")

                # Add individual file errors with cleaner formatting
                for lint_file in failed_files[:3]:  # Show first 3 files
                    error_msg = lint_file.stderr.strip() or lint_file.stdout.strip()

                    # Add file name
                    commands_with_issues.append(f"\n`{lint_file.file}`\n")

                    if error_msg:
                        # Take first 5 lines of error for better context
                        error_lines = error_msg.split("\n")
                        if error_lines:
                            commands_with_issues.append("```\n" + "\n".join(error_lines) + "\n```")

                    # Add separator between files (except for last one)
                    if lint_file != failed_files[min(2, len(failed_files) - 1)]:
                        commands_with_issues.append("---")

                # Show count if more files have errors
                if len(failed_files) > 3:
                    commands_with_issues.append(f"... and {len(failed_files) - 3} more files with errors")

        # Create markdown string for summary
        num_commands = len(lint_commands)
        markdown_content = f"**Files processed:** {total_files} executions across {num_commands} command{'s' if num_commands != 1 else ''}\n\n"

        if total_issues == 0:
            markdown_content += "**No issues found**"
        else:
            markdown_content += f"**{total_issues} issues found**\n\n"
            for command_issue in commands_with_issues:
                markdown_content += f"{command_issue}\n"

        summary_text = Markdown(markdown_content)

        console = await self.make(ConsoleService)
        # Display panel
        console.print_panel(
            summary_text,
            title="[secondary]Lint[/secondary]",
        )

        if failed_commands:
            do_lint = console.confirm("Attempt to fix lint errors?")
            if do_lint is False or do_lint is None:
                return (False, failed_commands)
            else:
                return (True, failed_commands)

        return (False, [])

    async def lint_files(self, changed_files: List[Path]) -> List[LintCommand]:
        """Run configured linters on specified files.

        Args:
                file_paths: Specific files to lint

        Returns:
                Dict mapping command names to lists of issues found


        """
        console = await self.make(ConsoleService)

        git_service: GitService = await self.make(GitService)

        # Get git root directory for consistent command execution
        repo = await git_service.get_repo()
        git_root = repo.working_dir

        # Handle commands as a list of command strings
        if self._config.lint.enable and self._config.lint.commands:
            # outer status bar and progress bar
            status = console.console.status("Not started")
            bar_column = BarColumn(bar_width=None, table_column=Column(ratio=2))
            progress = Progress(bar_column, TaskProgressColumn(), transient=True, expand=True)
            with Live(
                console.panel(
                    Group(progress, status),
                    title="[secondary]Lint[/secondary]",
                ),
                console=console.console,
                transient=True,
            ):
                status.update("Start Linting")

                # Create array of command/file combinations
                lint_commands = []
                total_lint_commands = 0
                for command in self._config.lint.commands:
                    lint_files = []
                    for file_path in changed_files:
                        # Get the language for this file using Pygments
                        file_language = get_language_from_filename(str(file_path))

                        # Check if file should be processed by this command based on language
                        if command.languages:
                            # If "*" is in languages, process all files
                            if "*" not in command.languages:
                                # If languages are specified, only process files with matching language (case-insensitive)
                                if not file_language or file_language.lower() not in [
                                    lang.lower() for lang in command.languages
                                ]:
                                    continue
                        # If no languages specified, process all files

                        full_command = " ".join(command.command + [str(file_path)])
                        lint_files.append(
                            LintFile(
                                file=file_path,
                                full_command=full_command,
                                exit_code=0,
                                stdout="",
                                stderr="",
                            )
                        )
                        total_lint_commands += 1
                    lint_commands.append(
                        LintCommand(
                            command=command.command,
                            results=lint_files,
                        )
                    )

                task = progress.add_task("Linting", total=total_lint_commands)

                for command in lint_commands:
                    for i, lint_file in enumerate(command.results):
                        command_str = " ".join(command.command)
                        status.update(f"Running {command_str} on {lint_file.file}")
                        log.info(f"Executing lint command: {command_str} on {lint_file.file}")

                        updated_lint_file = await self._execute_lint_command(lint_file, git_root)
                        command.results[i] = updated_lint_file

                        progress.advance(task)

                status.update(f"Finished linting {len(changed_files)} files")

        await asyncio.sleep(0.2)

        return lint_commands

    def format_lint_errors(self, failed_commands: List[LintFile]) -> str:
        """Format lint errors into a string for AI consumption.

        Args:
                failed_commands: List of LintFile objects that failed linting

        Returns:
                Formatted string with lint errors wrapped in boundary tags

        Usage: `error_msg = service.format_lint_errors(failed_files)` -> format for AI
        """
        lint_errors = []
        for lint_file in failed_commands:
            error_msg = lint_file.stderr.strip() or lint_file.stdout.strip()

            lint_error_message = list_to_multiline_text(
                [
                    Boundary.open(BoundaryType.ERROR, meta={"type": "lint", "source": str(lint_file.file)}),
                    f"{error_msg}",
                    Boundary.close(BoundaryType.ERROR),
                ]
            )
            lint_errors.append(lint_error_message)

        joined_lint_errors = "**Fix The Following Lint Errors**\n\n" + "\n\n".join(lint_errors)
        return joined_lint_errors
