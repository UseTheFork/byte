import re
import subprocess
from pathlib import Path
from typing import List

from byte.core.mixins.user_interactive import UserInteractive
from byte.core.service.base_service import Service
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.prompt_format.schemas import (
    BlockStatus,
    EditFormatPrompts,
    ShellCommandBlock,
)
from byte.domain.prompt_format.service.shell_command_prompt import (
    shell_command_system,
    shell_practice_messages,
)


class ShellCommandService(Service, UserInteractive):
    """Service for parsing and executing shell commands from AI responses.

    Provides shell command execution capabilities that work alongside
    edit format blocks, allowing the AI to run tests, install packages,
    or perform other shell operations after file edits.

    Usage: `blocks = await service.handle(ai_response)`
    """

    prompts: EditFormatPrompts
    command_blocks: List[ShellCommandBlock]

    async def boot(self):
        """Initialize the shell command service with prompts and empty command list."""
        self.command_blocks = []
        self.prompts = EditFormatPrompts(system=shell_command_system, examples=shell_practice_messages)

    async def handle(self, content: str) -> List[ShellCommandBlock]:
        """Process content by parsing and executing shell command blocks.

        Extracts shell command blocks from the content, validates them,
        and executes them sequentially with user confirmation.

        Args:
                content: Raw content string containing shell command blocks

        Returns:
                List of ShellCommandBlock objects representing executed commands

        Usage: `blocks = await service.handle(ai_response)`
        """
        blocks = self.parse_content_to_blocks(content)
        blocks = await self.execute_blocks(blocks)
        return blocks

    def parse_content_to_blocks(self, content: str) -> List[ShellCommandBlock]:
        """Extract shell command blocks from AI response content.

        Parses code fence blocks with 'sh' or 'bash' language identifiers
        and extracts the command content. Each line becomes a separate command.

        Args:
                content: Raw content string containing shell command blocks

        Returns:
                List of ShellCommandBlock objects parsed from the content

        Usage: `blocks = service.parse_content_to_blocks(ai_response)`
        """
        blocks = []

        # Pattern to match shell command blocks: ```sh or ```bash
        pattern = r"```(?:sh|bash)\n(.*?)```"

        matches = re.findall(pattern, content, re.DOTALL)

        for match in matches:
            # Split commands by newline, strip whitespace, filter empty lines
            commands = [cmd.strip() for cmd in match.strip().split("\n") if cmd.strip()]

            # Create a block for each command
            for command in commands:
                # Set working directory to project root if available
                working_dir = ""
                if self._config and self._config.project_root:
                    working_dir = str(self._config.project_root)

                blocks.append(
                    ShellCommandBlock(
                        command=command,
                        working_dir=working_dir,
                        block_status=BlockStatus.VALID,
                    )
                )

        return blocks

    def remove_blocks_from_content(self, content: str) -> str:
        """Remove shell command blocks from content and replace with summary message.

        Identifies all shell command blocks in the content and replaces them with
        a concise message indicating commands were executed. Preserves any text
        outside of the blocks.

        Args:
                content: Content string containing shell command blocks

        Returns:
                str: Content with blocks replaced by summary messages

        Usage: `cleaned = service.remove_blocks_from_content(ai_response)`
        """
        # Pattern to match shell command blocks
        pattern = r"```(?:sh|bash)\n(.*?)```"

        def replacement(match):
            commands = [cmd.strip() for cmd in match.group(1).strip().split("\n") if cmd.strip()]
            if len(commands) == 1:
                return f"*[Executed command: `{commands[0]}` - shell block removed]*"
            return f"*[Executed {len(commands)} commands - shell block removed]*"

        # Replace all blocks with summary messages
        cleaned_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

        return cleaned_content

    async def execute_blocks(self, blocks: List[ShellCommandBlock]) -> List[ShellCommandBlock]:
        """Execute validated shell command blocks sequentially.

        Prompts user for confirmation before executing each command.
        Commands are executed in the project root directory if configured.

        Args:
                blocks: List of ShellCommandBlock objects to execute

        Returns:
                List[ShellCommandBlock]: The original list of blocks with execution status

        Usage: `await service.execute_blocks(parsed_blocks)`
        """
        for block in blocks:
            # Only execute valid blocks
            if block.block_status != BlockStatus.VALID:
                continue

            # Prompt for confirmation
            if not await self.prompt_for_confirmation(
                f"Execute command: `{block.command}`?",
                True,
            ):
                block.status_message = "Execution skipped by user"
                continue

            try:
                # Determine working directory
                cwd = Path(block.working_dir) if block.working_dir else Path.cwd()

                # Execute the command
                result = subprocess.run(
                    block.command,
                    shell=True,
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                )

                # Display the result of the command in a panel
                console = await self.make(ConsoleService)

                if result.returncode == 0:
                    # Success - show output in green panel
                    block.status_message = f"Success: {result.stdout.strip()}"

                    output = result.stdout.strip()
                    if output:
                        syntax = console.syntax(
                            output,
                            "text",
                            word_wrap=True,
                        )
                        panel = console.panel(
                            syntax,
                            title=f"[bold green]Command Output: {block.command}[/bold green]",
                            border_style="green",
                        )
                        console.print(panel)
                else:
                    # Failure - show error in red panel
                    block.status_message = f"Failed (exit {result.returncode}): {result.stderr.strip()}"

                    error_output = result.stderr.strip()
                    if error_output:
                        syntax = console.syntax(
                            error_output,
                            "text",
                            word_wrap=True,
                        )
                        panel = console.panel(
                            syntax,
                            title=f"[bold red]Command Failed (exit {result.returncode}): {block.command}[/bold red]",
                            border_style="red",
                        )
                        console.print(panel)

            except subprocess.TimeoutExpired:
                block.status_message = "Command timed out after 5 minutes"
            except (OSError, subprocess.SubprocessError) as e:
                block.status_message = f"Execution error: {e!s}"

        return blocks
