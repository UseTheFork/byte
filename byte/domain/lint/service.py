import asyncio
from os import PathLike
from typing import Dict, List, Union

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.spinner import Spinner
from rich.text import Text

from byte.context import make
from byte.core.config.mixins import Configurable
from byte.core.service.mixins import Bootable
from byte.domain.agent.commit.events import PreCommitStarted
from byte.domain.git.service import GitService


class LintService(Bootable, Configurable):
    """Domain service for code linting and formatting operations.

    Orchestrates multiple linting commands configured in config.yaml to analyze
    and optionally fix code quality issues. Integrates with git service to
    target only changed files for efficient linting workflows.
    Usage: `await lint_service.lint_changed_files()` -> runs configured linters on git changes
    """

    async def lint_changed_files(self) -> Dict[str, List[str]]:
        """Run configured linters on git changed files.

        Returns:
            Dict mapping command names to lists of issues found

        Usage: `results = await lint_service.lint_changed_files()` -> lint changed files
        """
        console: Console = await make(Console)
        git_service: GitService = await make(GitService)
        changed_files = await git_service.get_changed_files()

        # Get git root directory for consistent command execution
        repo = await git_service.get_repo()
        git_root = repo.working_dir

        results = {}

        # Handle commands as a list of command strings
        if self._config.auto_lint and self._config.lint_commands:
            spinner = Spinner("dots", text="Running linters...")
            with Live(spinner, console=console, transient=True, refresh_per_second=10):
                for i, command_template in enumerate(self._config.lint_commands):
                    command_name = f"command_{i}"
                    results[command_name] = []

                    # Iterate over each changed file
                    for file_path in changed_files:
                        # Update spinner to show current command and file
                        spinner.update(
                            text=f"Running {command_template} on {file_path}"
                        )

                        # Build the command with the file path
                        cmd = f"{command_template} {file_path!s}"

                        try:
                            # Run the command and capture output
                            process = await asyncio.create_subprocess_shell(
                                cmd,
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE,
                                cwd=git_root,
                            )

                            stdout, stderr = await process.communicate()
                            exit_code = process.returncode

                            # Store the result
                            result = {
                                "file": str(file_path),
                                "command": cmd,
                                "exit_code": exit_code,
                                "stdout": stdout.decode("utf-8", errors="ignore"),
                                "stderr": stderr.decode("utf-8", errors="ignore"),
                            }

                            results[command_name].append(result)

                        except Exception as e:
                            # Handle command execution errors
                            error_result = {
                                "file": str(file_path),
                                "command": cmd,
                                "exit_code": -1,
                                "stdout": "",
                                "stderr": f"Error executing command: {e!s}",
                            }
                            results[command_name].append(error_result)

        # Display summary panel with results
        self._display_results_summary(console, results)

        return results

    def _display_results_summary(
        self, console: Console, results: Dict[str, List[str]]
    ) -> None:
        """Display a summary panel of linting results.

        Args:
            console: Rich console for output
            results: Dictionary of linting results by command
        """
        if not results:
            return

        # Count total files processed and issues found
        total_files = 0
        total_issues = 0
        commands_with_issues = []

        for _, command_results in results.items():
            files_processed = len(command_results)
            total_files += files_processed

            # Count issues (non-zero exit codes)
            issues_found = sum(
                1 for result in command_results if result.get("exit_code", 0) != 0
            )
            total_issues += issues_found

            if issues_found > 0:
                # Group issues by command template for better display
                command_issues = {}
                command_errors = {}
                for result in command_results:
                    if result.get("exit_code", 0) != 0:
                        cmd = result.get("command", "").split()[0]  # Get base command
                        file_name = result.get("file", "")
                        if cmd not in command_issues:
                            command_issues[cmd] = []
                            command_errors[cmd] = []
                        command_issues[cmd].append(file_name)

                        # Collect error details
                        error_output = result.get("stderr", "").strip()
                        if not error_output:
                            error_output = result.get("stdout", "").strip()
                        if error_output:
                            command_errors[cmd].append(f"{file_name}: {error_output}")

                # Add formatted command issues with errors
                for cmd, files in command_issues.items():
                    if len(files) == 1:
                        commands_with_issues.append(f"{cmd} on {files[0]}")
                    else:
                        commands_with_issues.append(f"{cmd} on {len(files)} files")

                    # Add error details for this command
                    if command_errors.get(cmd):
                        for error in command_errors[cmd][:3]:  # Limit to first 3 errors
                            commands_with_issues.append(f"    {error}")
                        if len(command_errors[cmd]) > 3:
                            commands_with_issues.append(
                                f"    ... and {len(command_errors[cmd]) - 3} more errors"
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
            title="[bold]Lint Results[/bold]",
            border_style="blue",
            padding=(0, 1),
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

    async def _handle_pre_commit(self, event: PreCommitStarted) -> None:
        """Handle pre-commit event by running linters on staged files.

        Automatically runs configured linters when a commit process begins,
        ensuring code quality before commits are created.
        Usage: Called automatically when PreCommitStarted event is emitted
        """

        await self.lint_changed_files()
