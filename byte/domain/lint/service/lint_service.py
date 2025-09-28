import asyncio
from os import PathLike
from typing import Dict, List, Union

from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TaskProgressColumn
from rich.table import Column
from rich.text import Text

from byte.core.service.base_service import Service
from byte.domain.git.service.git_service import GitService
from byte.domain.lint.types import LintCommand, LintFile


class LintService(Service):
    """Domain service for code linting and formatting operations.

    Orchestrates multiple linting commands configured in config.yaml to analyze
    and optionally fix code quality issues. Integrates with git service to
    target only changed files for efficient linting workflows.
    Usage: `await lint_service.lint_changed_files()` -> runs configured linters on git changes
    """

    async def handle(self, **kwargs):
        """Handle lint service execution - main entry point for linting operations."""
        return await self.lint_changed_files()

    async def lint_changed_files(self) -> List[LintCommand]:
        """Run configured linters on git changed files.

        Returns:
            List of LintCommand objects with results

        Usage: `results = await lint_service.lint_changed_files()` -> lint changed files
        """
        console: Console = await self.make(Console)

        git_service: GitService = await self.make(GitService)
        all_changed_files = await git_service.get_changed_files()

        # Filter out removed files - only lint files that actually exist
        changed_files = [f for f in all_changed_files if f.exists()]

        # Get git root directory for consistent command execution
        repo = await git_service.get_repo()
        git_root = repo.working_dir

        # Handle commands as a list of command strings
        if self._config.lint.enable and self._config.lint.commands:
            # outer status bar and progress bar
            status = console.status("Not started")
            bar_column = BarColumn(bar_width=None, table_column=Column(ratio=2))
            progress = Progress(
                bar_column, TaskProgressColumn(), transient=True, expand=True
            )
            with Live(
                Panel(
                    Group(progress, status),
                    title="Lint",
                    title_align="left",
                    border_style="secondary",
                ),
                console=console,
                transient=True,
            ):
                status.update("[bold primary]Start Linting")

                # Create array of command/file combinations
                lint_commands = []
                total_lint_commands = 0
                for command in self._config.lint.commands:
                    lint_files = []
                    for file_path in changed_files:
                        # Check if file should be processed by this command based on extensions
                        if command.extensions:
                            # If extensions are specified, only process files with matching extensions
                            if not any(
                                str(file_path).endswith(ext)
                                for ext in command.extensions
                            ):
                                continue
                        # If no extensions specified, process all files

                        lint_files.append(
                            LintFile(
                                file=file_path,
                                full_command=f"{command.command} {file_path!s}",
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
                        status.update(f"Running {command.command} on {lint_file.file}")

                        updated_lint_file = await self._execute_lint_command(
                            lint_file, git_root
                        )
                        command.results[i] = updated_lint_file

                        progress.advance(task)

                status.update(
                    f"[bold primary]Finished linting {len(changed_files)} files"
                )

        # Display summary panel with results
        self._display_results_summary(console, lint_commands)

        return lint_commands

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

    def _display_results_summary(
        self, console: Console, lint_commands: List[LintCommand]
    ) -> None:
        """Display a summary panel of linting results.

        Args:
            console: Rich console for output
            lint_commands: List of LintCommand objects with results
        """
        if not lint_commands:
            return

        # Count total files processed and issues found
        total_files = 0
        total_issues = 0
        commands_with_issues = []

        # TODO: Find a better way to display this. Not crazy about it.

        for command in lint_commands:
            files_processed = len(command.results)
            total_files += files_processed

            # Count issues (non-zero exit codes)
            issues_found = sum(
                1 for lint_file in command.results if lint_file.exit_code != 0
            )
            total_issues += issues_found

            if issues_found > 0:
                # Collect files with issues for this command
                files_with_issues = []
                error_details = []

                for lint_file in command.results:
                    if lint_file.exit_code != 0:
                        files_with_issues.append(str(lint_file.file))

                        # Collect error details
                        error_output = lint_file.stderr.strip()
                        if not error_output:
                            error_output = lint_file.stdout.strip()
                        if error_output:
                            error_details.append(f"{lint_file.file}: {error_output}")

                # Add formatted command issues
                if len(files_with_issues) == 1:
                    commands_with_issues.append(
                        f"{command.command} on {files_with_issues[0]}"
                    )
                else:
                    commands_with_issues.append(
                        f"{command.command} on {len(files_with_issues)} files"
                    )

                # Add error details (limit to first 3)
                for error in error_details[:3]:
                    commands_with_issues.append(f"    {error}")
                if len(error_details) > 3:
                    commands_with_issues.append(
                        f"    ... and {len(error_details) - 3} more errors"
                    )

        # Create summary text
        summary_text = Text()
        summary_text.append(f"Files processed: {total_files}\n", style="dim")

        if total_issues == 0:
            summary_text.append("No issues found", style="green bold")
        else:
            summary_text.append(f"{total_issues} issues found\n", style="yellow bold")
            for command_issue in commands_with_issues:
                summary_text.append(f"  • {command_issue}\n", style="yellow")

        # Display panel
        panel = Panel(
            summary_text,
            title="Lint",
            title_align="left",
            border_style="secondary",
        )
        console.print(panel)

    async def lint_files(
        self, file_paths: List[Union[str, PathLike]]
    ) -> Dict[str, List[str]]:
        """Run configured linters on specified files.

        Args:
            file_paths: Specific files to lint

        Returns:
            Dict mapping command names to lists of issues found

        Usage: `results = await lint_service.lint_files(["main.py", "utils.py"])`
        """
        # TODO: Implement linting of specific files
        return {}
