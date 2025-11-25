from typing import List

from byte.core.config.config import ByteConfg
from byte.core.mixins.user_interactive import UserInteractive
from byte.core.service.base_service import Service
from byte.domain.prompt_format.parser.pseudo_xml.service import PseudoXmlParserService
from byte.domain.prompt_format.schemas import (
    EditFormatPrompts,
    SearchReplaceBlock,
)
from byte.domain.prompt_format.service.shell_command_prompt import (
    shell_command_system,
    shell_practice_messages,
)


class EditFormatService(Service, UserInteractive):
    """Orchestrates edit format operations including file edits and optional shell commands.

    Combines edit block processing with shell command execution based on configuration.
    When shell commands are enabled, provides unified prompts that include both capabilities.
    Shell commands are only executed after all file edits successfully complete.

    Usage: `blocks = await service.handle(ai_response)`
    """

    async def boot(self):
        """Initialize service with appropriate prompts based on configuration."""
        config = await self.make(ByteConfg)
        self.edit_block_service = await self.make(PseudoXmlParserService)

        if config.edit_format.enable_shell_commands:
            # Combine system prompts to provide AI with both edit and shell capabilities
            combined_system = f"{self.edit_block_service.prompts.system}\n\n{shell_command_system}"

            # Combine practice messages to show examples of both edit blocks and shell commands
            combined_examples = self.edit_block_service.prompts.examples + shell_practice_messages

            self.prompts = EditFormatPrompts(system=combined_system, examples=combined_examples)
        else:
            self.prompts = EditFormatPrompts(
                system=self.edit_block_service.prompts.system, examples=self.edit_block_service.prompts.examples
            )

    async def validate(self, content: str) -> List[SearchReplaceBlock]:
        """Process content by validating, parsing, and applying edit blocks and shell commands.

        First processes all file edit blocks through the complete workflow (validation,
        parsing).

        Args:
                content: Raw content string containing edit instructions and optional shell commands

        Returns:
                List of SearchReplaceBlock objects representing individual edit operations

        Raises:
                PreFlightCheckError: If content contains malformed edit blocks

        Usage: `blocks = await service.validate(ai_response)`
        """

        # Process file edit blocks
        blocks = await self.edit_block_service.handle(content)

        return blocks

    async def apply(self, blocks: List[SearchReplaceBlock]) -> List[SearchReplaceBlock]:
        """Process content by validating, parsing, and applying edit blocks and shell commands.

        First processes all file edit blocks through the complete workflow (validation,
        parsing). Then, if shell commands are enabled and all edits succeeded,
        executes any shell command blocks found in the content."""

        # Process file edit blocks
        blocks = await self.edit_block_service.apply_blocks(blocks)

        # Only execute shell commands if enabled and all edit blocks succeeded
        # if self._config.edit_format.enable_shell_commands:
        #     all_edits_valid = all(b.block_status == BlockStatus.VALID for b in blocks)

        #     if all_edits_valid:
        #         shell_command_service = await self.make(ShellCommandService)
        #         await shell_command_service.handle(content)
        #     else:
        #         # Log that shell commands were skipped due to failed edits

        #         log.info("Skipping shell command execution due to failed edit blocks")

        return blocks
