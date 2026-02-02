import asyncio
from typing import Optional

from byte.cli import InputCancelledError, SubprocessResult
from byte.support import Service
from byte.support.mixins import UserInteractive
from byte.support.utils import list_to_multiline_text


class SubprocessService(Service, UserInteractive):
    """Service for executing subprocess commands with async support.

    Provides a clean interface for running shell commands asynchronously and
    capturing their output, exit codes, and errors in a structured format.

    Usage: `result = await subprocess_service.run("ls -la")` -> execute command
    """

    async def run(
        self,
        command: str,
        timeout: Optional[float] = None,
    ) -> SubprocessResult:
        """Execute a shell command and return structured results.

        Always runs commands from the project root directory.

        Args:
                command: Shell command to execute
                timeout: Optional timeout in seconds

        Returns:
                SubprocessResult with exit code, stdout, stderr, and metadata

        Usage: `result = await service.run("echo hello")`
        Usage: `result = await service.run("pytest", timeout=30.0)`
        """
        try:
            # Get project root from config
            working_dir = str(self.app["path"])

            # Create subprocess
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir,
            )

            # Run with optional timeout
            if timeout:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout,
                )
            else:
                stdout, stderr = await process.communicate()

            exit_code = process.returncode

            return SubprocessResult(
                exit_code=exit_code if exit_code is not None else -1,
                stdout=stdout.decode("utf-8", errors="ignore"),
                stderr=stderr.decode("utf-8", errors="ignore"),
                command=command,
                cwd=working_dir,
            )

        except TimeoutError:
            # Handle timeout
            return SubprocessResult(
                exit_code=-1,
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
                command=command,
                cwd=working_dir,
            )

        except Exception as e:
            # Handle other execution errors
            return SubprocessResult(
                exit_code=-1,
                stdout="",
                stderr=f"Error executing command: {e!s}",
                command=command,
                cwd=working_dir,
            )

    async def _display_subprocess_results(self, subprocess_result) -> tuple[bool, Optional[str]]:
        """Display subprocess execution results and prompt user to add to messages.

        Shows the command output in a panel and asks if the user wants to include
        the results in the conversation context for AI awareness.

        Usage: `await self._display_subprocess_results(result)` -> displays and prompts
        """
        console = self.app["console"]

        # Display the results with more detail
        result_display = f"Exit Code: {subprocess_result.exit_code}\n\nOutput:\n{subprocess_result.stdout}"
        if subprocess_result.stderr:
            result_display += f"\n\nErrors:\n{subprocess_result.stderr}"

        console.print_panel(result_display, title=f"Command: {subprocess_result.command}")

        try:
            # Ask user if they want to add results to messages
            should_add = await self.prompt_for_confirmation(
                "Add subprocess output to conversation context?",
                default=True,
            )

            user_input = None
            if should_add:
                # Ask user if they want to add results to messages
                add_note = await self.prompt_for_confirmation(
                    "Add a note?",
                    default=True,
                )
                if add_note:
                    try:
                        user_input = await self.prompt_for_input(
                            "Message to include with the output",
                        )
                    except InputCancelledError:
                        pass

            return should_add, user_input
        except InputCancelledError:
            return False, None

    async def run_and_confirm(self, command: str) -> str | None:
        """Display subprocess execution results and prompt user to add to messages.

        Shows the command output in a panel and asks if the user wants to include
        the results in the conversation context for AI awareness.

        Usage: `await self._display_subprocess_results(result)` -> displays and prompts
        """

        subprocess_result = await self.run(command)
        should_add, user_input = await self._display_subprocess_results(subprocess_result)

        if should_add:
            # Format the result using XML-like syntax
            result_message = [
                f"Below is the stdout of running `{subprocess_result.command}` that resulted in a exit code of {subprocess_result.exit_code!s}",
                "```text",
                subprocess_result.stdout,
                "```",
                "",
            ]

            if subprocess_result.stderr:
                result_message.append("Here is the stderr:")
                result_message.append("```text")
                result_message.append(subprocess_result.stderr)
                result_message.append("```")
                result_message.append("")

            if user_input:
                result_message.append("")
                result_message.append(user_input)

            return list_to_multiline_text(result_message)

        return None
