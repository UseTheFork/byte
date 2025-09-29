import asyncio
from pathlib import Path
from typing import List

from rich.console import Console, Group
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TaskProgressColumn
from rich.table import Column

from byte import dd
from byte.core.mixins.user_interactive import UserInteractive
from byte.core.service.base_service import Service
from byte.domain.git.service.git_service import GitService
from byte.domain.lint.types import LintCommand, LintFile


class LintService(Service, UserInteractive):
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

    async def _display_results_summary(
        self, console: Console, lint_commands: List[LintCommand]
    ) -> None:
        """Display a summary panel of linting results.

        Args:
            console: Rich console for output
            lint_commands: List of LintCommand objects with results
        """
        from byte.domain.agent.implementations.fixer.agent import FixerAgent

        if not lint_commands:
            return

        # Count total files processed and issues found
        total_files = 0
        total_issues = 0
        commands_with_issues = []
        failed_commands = []

        for command in lint_commands:
            total_files += len(command.results)

            # Get files with issues for this command
            failed_files = [
                lint_file for lint_file in command.results if lint_file.exit_code != 0
            ]

            if failed_files:
                total_issues += len(failed_files)

                # Append failed files to failed_commands list
                failed_commands.extend(failed_files)

                # Add command header
                commands_with_issues.append(
                    f"# **{command.command}** ({len(failed_files)} files)\n"
                )

                # Add individual file errors with cleaner formatting
                for lint_file in failed_files[:3]:  # Show first 3 files
                    error_msg = lint_file.stderr.strip() or lint_file.stdout.strip()

                    # Add file name
                    commands_with_issues.append(f"\n`{lint_file.file}`\n")

                    if error_msg:
                        # Take first 5 lines of error for better context
                        error_lines = error_msg.split("\n")
                        if error_lines:
                            commands_with_issues.append(
                                "```\n" + "\n".join(error_lines) + "\n```"
                            )

                    # Add separator between files (except for last one)
                    if lint_file != failed_files[min(2, len(failed_files) - 1)]:
                        commands_with_issues.append("---")

                # Show count if more files have errors
                if len(failed_files) > 3:
                    commands_with_issues.append(
                        f"... and {len(failed_files) - 3} more files with errors"
                    )

        # Create markdown string for summary
        markdown_content = f"**Files processed:** {total_files}\n\n"

        if total_issues == 0:
            markdown_content += "**No issues found**"
        else:
            markdown_content += f"**{total_issues} issues found**\n\n"
            for command_issue in commands_with_issues:
                markdown_content += f"{command_issue}\n"

        summary_text = Markdown(markdown_content)

        # Display panel
        panel = Panel(
            summary_text,
            title="Lint",
            title_align="left",
            border_style="secondary",
        )
        console.print(panel)

        # Offer user a chance to fix issues if any were found
        if failed_commands:
            do_lint = await self.prompt_for_confirmation("Attempt to fix lint errors?")
            if do_lint:
                for lint_file in failed_commands:
                    fixer_agent = await self.make(FixerAgent)
                    error_msg = lint_file.stderr.strip() or lint_file.stdout.strip()
                    lint_error_message = f"""# Fix The Folllwing Lint Error
                    File: {lint_file.file}\n
                    Error:
                    ```
                    {error_msg}
                    ```
                    """
                    fixer_agent = await fixer_agent.execute(
                        request={"messages": [("user", lint_error_message)]}
                    )
                    dd(fixer_agent)

    async def lint_files(self, changed_files: List[Path]) -> List[LintCommand]:
        """Run configured linters on specified files.

        Args:
            file_paths: Specific files to lint

        Returns:
            Dict mapping command names to lists of issues found


        """
        console: Console = await self.make(Console)

        git_service: GitService = await self.make(GitService)

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
        await self._display_results_summary(console, lint_commands)

        return lint_commands
