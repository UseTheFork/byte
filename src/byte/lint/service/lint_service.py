import asyncio
from pathlib import Path
from typing import List

from byte import Service
from byte.git import GitService
from byte.lint import LintConfigException, LintTask
from byte.support import Boundary, BoundaryType
from byte.support.mixins import UserInteractive
from byte.support.utils import get_language_from_filename, list_to_multiline_text
from byte.tui import Messages, Status


class LintService(Service, UserInteractive):
    """Orchestrate linting and formatting operations on configured files."""

    async def validate(self) -> bool:
        """Validate lint service configuration before execution."""
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

    async def handle(self, **kwargs) -> List[LintTask]:
        """Run configured linters on git changed files."""

        git_service = self.app.make(GitService)
        all_changed_files = await git_service.get_changed_files()
        self.app["log"].info(all_changed_files)

        return await self.lint_files(all_changed_files)

    async def _execute_lint_task(self, lint_task: LintTask, git_root: str) -> LintTask:
        """Execute a lint command with all batched files and capture output."""
        try:
            # Run the command and capture output
            process = await asyncio.create_subprocess_exec(
                *lint_task.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=git_root,
            )

            stdout, stderr = await process.communicate()
            exit_code = process.returncode

            self.app["log"].debug(
                "Executed lint command: {} in {} with exit code {}",
                " ".join(lint_task.command),
                git_root,
                exit_code,
            )
            self.app["log"].debug("stdout: {}", stdout.decode("utf-8", errors="ignore"))
            self.app["log"].debug("stderr: {}", stderr.decode("utf-8", errors="ignore"))

            lint_task.exit_code = exit_code
            lint_task.stdout = stdout.decode("utf-8", errors="ignore")
            lint_task.stderr = stderr.decode("utf-8", errors="ignore")

        except Exception as e:
            # Handle command execution errors
            lint_task.exit_code = -1
            lint_task.stderr = f"Error executing command: {e!s}"

        # Return updated LintTask with results
        return lint_task

    async def display_results_summary(self, lint_results: List[LintTask]) -> tuple[bool, list]:
        """Display a summary panel of linting results."""

        if not lint_results:
            return (False, [])

        # Count total files processed and issues found
        total_issues = 0
        commands_with_issues = []
        failed_commands = []

        # Get commands with issues
        failed_cmds = [lint_cmd for lint_cmd in lint_results if lint_cmd.exit_code != 0]

        if failed_cmds:
            total_issues += len(failed_cmds)

            # Append failed commands to failed_commands list
            failed_commands.extend(failed_cmds)

            # Group by command string
            for lint_cmd in failed_cmds:
                command_str = " ".join(lint_cmd.command)

                # Add command header
                commands_with_issues.append(f"# **{command_str}** ({len(lint_cmd.files)} files)\n")

                # Add individual file list with cleaner formatting
                for file_path in lint_cmd.files[:3]:  # Show first 3 files
                    commands_with_issues.append(f"\n`{file_path}`\n")

                    # Add separator between files (except for last one)
                    if file_path != lint_cmd.files[min(2, len(lint_cmd.files) - 1)]:
                        commands_with_issues.append("---")

                # Extract error message from stdout/stderr
                error_msg = lint_cmd.stderr.strip() or lint_cmd.stdout.strip()
                if error_msg:
                    # Take first 5 lines of error for better context
                    error_lines = error_msg.split("\n")
                    if error_lines:
                        commands_with_issues.append("```\n" + "\n".join(error_lines[:5]) + "\n```")

                # Show count if more files have errors
                if len(lint_cmd.files) > 3:
                    commands_with_issues.append(f"... and {len(lint_cmd.files) - 3} more files")

        # Create markdown string for summary
        num_commands = len(lint_results)
        markdown_content = f"**Commands executed:** {num_commands}\n\n"

        if total_issues == 0:
            markdown_content += "**No issues found**"
        else:
            markdown_content += f"**{total_issues} commands with issues**\n\n"
            for command_issue in commands_with_issues:
                markdown_content += f"{command_issue}\n"

        # Display panel via TUI
        self.emit_tui(
            Messages.LintResults(
                str(markdown_content),
                total_issues,
            )
        )

        if failed_commands:
            do_lint = await self.prompt_for_confirmation("Attempt to fix lint errors?")
            if do_lint is False or do_lint is None:
                return (False, failed_commands)
            else:
                return (True, failed_commands)

        return (False, [])

    async def lint_files(self, changed_files: List[Path]) -> List[LintTask]:
        """Run configured linters on specified files."""
        # Filter out deleted/missing files - only lint files that exist on disk
        changed_files = [f for f in changed_files if f.exists()]

        if not changed_files:
            return []

        git_service: GitService = self.app.make(GitService)

        # Get git root directory for consistent command execution
        repo = await git_service.get_repo()
        git_root = repo.working_dir

        lint_commands_to_execute: List[LintTask] = []

        # Handle commands as a list of command strings
        if self.app["config"].lint.enable and self.app["config"].lint.commands:
            # Group files by command (outer loop over commands)
            for config_command in self.app["config"].lint.commands:
                matching_files: List[Path] = []

                # Collect all files that match this command's language filter
                for file_path in changed_files:
                    # Get the language for this file using Pygments
                    file_language = get_language_from_filename(str(file_path))

                    # Check if file should be processed by this command based on language
                    if config_command.languages:
                        # If "*" is in languages, process all files
                        if "*" not in config_command.languages:
                            # If languages are specified, only process files with matching language (case-insensitive)
                            if not file_language or file_language.lower() not in [
                                lang.lower() for lang in config_command.languages
                            ]:
                                continue
                    # If no languages specified, process all files

                    matching_files.append(file_path)

                # Only create a LintTask if there are matching files
                if matching_files:
                    # Build command with {files} placeholder replacement
                    command_parts = list(config_command.command)  # Copy command template

                    # Check if any command part contains {files} placeholder
                    has_files_placeholder = any("{files}" in part for part in command_parts)

                    if has_files_placeholder:
                        # Replace {files} placeholder by splicing file paths into that position
                        expanded_command = []
                        for part in command_parts:
                            if "{files}" in part:
                                # Splice in all file paths at this position
                                expanded_command.extend(str(f) for f in matching_files)
                            else:
                                expanded_command.append(part)
                        command_parts = expanded_command
                    else:
                        # Fallback to appending all files at end
                        command_parts.extend(str(f) for f in matching_files)

                    # Create single LintTask for this command with all matching files
                    lint_cmd = LintTask(
                        command=command_parts,
                        files=matching_files,
                        exit_code=0,
                    )
                    lint_commands_to_execute.append(lint_cmd)

            # Calculate total commands for progress tracking
            self._total_commands = len(lint_commands_to_execute)
            self._completed_count = 0

            self.app["log"].info(changed_files)

            # Emit lint started event
            self.emit_tui(
                Messages.Lint(
                    status=Status.PENDING,
                    total_commands=self._total_commands,
                )
            )

            # Execute all batched commands in parallel
            if lint_commands_to_execute:
                command_tasks = [
                    self._execute_lint_task(lint_cmd, str(git_root)) for lint_cmd in lint_commands_to_execute
                ]

                results = await asyncio.gather(*command_tasks)

                # Emit lint completed event
                failed_count = len([r for r in results if r.exit_code != 0])
                self.emit_tui(
                    Messages.Lint(
                        status=Status.SUCCESS,
                        total_files=len(changed_files),
                        failed_files=failed_count,
                        success=failed_count == 0,
                    )
                )
            else:
                results = []
        else:
            results = []

        await asyncio.sleep(0.2)

        return results

    def format_lint_errors(self, failed_commands: List[LintTask]) -> str:
        """Format lint errors into a string for AI consumption."""
        lint_errors = []
        for lint_cmd in failed_commands:
            error_msg = lint_cmd.stderr.strip() or lint_cmd.stdout.strip()

            # Create error message for all files in this command
            file_list = ", ".join(str(f) for f in lint_cmd.files)
            lint_error_message = list_to_multiline_text(
                [
                    Boundary.open(BoundaryType.ERROR, meta={"type": "lint", "source": file_list}),
                    f"{error_msg}",
                    Boundary.close(BoundaryType.ERROR),
                ]
            )
            lint_errors.append(lint_error_message)

        joined_lint_errors = "**Fix The Following Lint Errors**\n\n" + "\n\n".join(lint_errors)
        return joined_lint_errors
