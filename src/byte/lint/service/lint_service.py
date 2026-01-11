import asyncio
from pathlib import Path
from typing import List

from rich.console import Group
from rich.live import Live
from rich.progress import BarColumn, Progress, TaskID, TextColumn
from rich.table import Column

from byte import Service
from byte.cli import Markdown
from byte.git import GitService
from byte.lint import LintConfigException, LintFile
from byte.prompt_format import Boundary, BoundaryType
from byte.support.mixins import UserInteractive
from byte.support.utils import get_language_from_filename, list_to_multiline_text


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
        if not self.app["config"].lint.enable:
            raise LintConfigException(
                "Linting is disabled. Set 'lint.enable' to true in your .byte/config.yaml to use lint commands."
            )

        if len(self.app["config"].lint.commands) == 0:
            raise LintConfigException(
                "No lint commands configured. Add commands to 'lint.commands' in your .byte/config.yaml. "
                "See docs/reference/settings.md for configuration examples."
            )

        return True

    async def handle(self, **kwargs) -> List[LintFile]:
        """Handle lint service execution - main entry point for linting operations."""

        return await self.lint_changed_files()

    async def lint_changed_files(self) -> List[LintFile]:
        """Run configured linters on git changed files.

        Returns:
                List of LintCommandType objects with results

        Usage: `results = await lint_service.lint_changed_files()` -> lint changed files
        """

        git_service = self.app.make(GitService)
        all_changed_files = await git_service.get_changed_files()

        # Filter out removed files - only lint files that actually exist
        changed_files = [f for f in all_changed_files if f.exists()]

        return await self.lint_files(changed_files)

    async def _execute_lint_command(self, lint_file: LintFile, task_id: TaskID, git_root) -> LintFile:
        try:
            # Run the command and capture output
            process = await asyncio.create_subprocess_shell(
                lint_file.full_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=git_root,
            )

            self._progress.update(task_id, advance=1)

            stdout, stderr = await process.communicate()
            exit_code = process.returncode

            self.app["log"].debug(
                "Executed lint command: {} in {} with exit code {}",
                lint_file.full_command,
                git_root,
                exit_code,
            )
            self.app["log"].debug("stdout: {}", stdout.decode("utf-8", errors="ignore"))
            self.app["log"].debug("stderr: {}", stderr.decode("utf-8", errors="ignore"))

            lint_file.exit_code = exit_code
            lint_file.stdout = stdout.decode("utf-8", errors="ignore")
            lint_file.stderr = stderr.decode("utf-8", errors="ignore")

            # Return updated LintFile with results
            return lint_file

        except Exception as e:
            # Handle command execution errors
            lint_file.exit_code = -1
            lint_file.stderr = f"Error executing command: {e!s}"
            return lint_file

    async def display_results_summary(self, lint_results: List[LintFile]) -> tuple[bool, list]:
        """Display a summary panel of linting results.

        Args:
                lint_commands: List of LintCommandType objects with results
        """

        if not lint_results:
            return (False, [])

        # Count total files processed and issues found
        total_issues = 0
        commands_with_issues = []
        failed_commands = []

        # Get files with issues for this command
        failed_files = [lint_file for lint_file in lint_results if lint_file.exit_code != 0]

        if failed_files:
            total_issues += len(failed_files)

            # Append failed files to failed_commands list
            failed_commands.extend(failed_files)

            # Group failed files by command
            from itertools import groupby

            # Sort by command first so groupby works correctly
            failed_files_sorted = sorted(failed_files, key=lambda lf: " ".join(lf.command))

            # Group by command
            for command_key, files_iter in groupby(failed_files_sorted, key=lambda lf: " ".join(lf.command)):
                files_for_command = list(files_iter)
                command_str = command_key

                # Add command header
                commands_with_issues.append(f"# **{command_str}** ({len(files_for_command)} files)\n")

                # Add individual file errors with cleaner formatting
                for lint_file in files_for_command[:3]:  # Show first 3 files
                    error_msg = lint_file.stderr.strip() or lint_file.stdout.strip()

                    # Add file name
                    commands_with_issues.append(f"\n`{lint_file.file}`\n")

                    if error_msg:
                        # Take first 5 lines of error for better context
                        error_lines = error_msg.split("\n")
                        if error_lines:
                            commands_with_issues.append("```\n" + "\n".join(error_lines) + "\n```")

                    # Add separator between files (except for last one)
                    if lint_file != files_for_command[min(2, len(files_for_command) - 1)]:
                        commands_with_issues.append("---")

                # Show count if more files have errors
                if len(files_for_command) > 3:
                    commands_with_issues.append(f"... and {len(files_for_command) - 3} more files with errors")

        # Create markdown string for summary
        num_commands = len(lint_results)
        markdown_content = f"**Files processed:** {num_commands} command executions\n\n"

        if total_issues == 0:
            markdown_content += "**No issues found**"
        else:
            markdown_content += f"**{total_issues} issues found**\n\n"
            for command_issue in commands_with_issues:
                markdown_content += f"{command_issue}\n"

        summary_text = Markdown(markdown_content)

        console = self.app["console"]
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

    # Group tasks by file, run commands sequentially per file, files in parallel
    async def _lint_file_sequential(self, file_path: Path, lint_files: List[LintFile], git_root: str) -> List[LintFile]:
        """Execute lint commands sequentially for a single file."""
        num_commands = len(lint_files)
        file_task_id = self._progress.add_task(f"{file_path.name}", total=num_commands)

        results = []
        for lint_file in lint_files:
            result = await self._execute_lint_command(lint_file, file_task_id, git_root)
            results.append(result)

        return results

    async def lint_files(self, changed_files: List[Path]) -> List[LintFile]:
        """Run configured linters on specified files.

        Args:
                file_paths: Specific files to lint

        Returns:
                Dict mapping command names to lists of issues found


        """
        console = self.app["console"]

        git_service: GitService = self.app.make(GitService)

        # Get git root directory for consistent command execution
        repo = await git_service.get_repo()
        git_root = repo.working_dir

        self._lint_stack = {}

        # Handle commands as a list of command strings
        if self.app["config"].lint.enable and self.app["config"].lint.commands:
            # outer status bar and progress bar
            status = console.console.status("Not started")
            bar_column = BarColumn(bar_width=None, table_column=Column(ratio=2))
            self._progress = Progress(
                TextColumn("[progress.description]{task.description}", table_column=Column(ratio=1)),
                bar_column,
                transient=True,
                expand=True,
            )
            with Live(
                console.panel(
                    Group(self._progress, status),
                    title="[secondary]Lint[/secondary]",
                ),
                console=console.console,
                transient=True,
            ):
                # Create array of command/file combinations
                status.update("Gathering Commands")
                for command in self.app["config"].lint.commands:
                    for file_path in changed_files:
                        if str(file_path) not in self._lint_stack:
                            self._lint_stack[str(file_path)] = []

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
                        self._lint_stack[str(file_path)].append(
                            LintFile(
                                command=command.command,
                                file=file_path,
                                full_command=full_command,
                                exit_code=0,
                            )
                        )

                status.update("Linting...")
                file_tasks = [
                    self._lint_file_sequential(Path(file_path_str), lint_files, git_root)
                    for file_path_str, lint_files in self._lint_stack.items()
                ]

                all_results = await asyncio.gather(*file_tasks)
                # Flatten results
                results = [result for file_results in all_results for result in file_results]

        await asyncio.sleep(0.2)

        return results

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
