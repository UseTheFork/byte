from typing import List

from byte.core.config.config import ByteConfg
from byte.core.logging import log
from byte.core.mixins.user_interactive import UserInteractive
from byte.core.service.base_service import Service
from byte.domain.edit_format.models import (
	BlockStatus,
	EditFormatPrompts,
	SearchReplaceBlock,
)
from byte.domain.edit_format.service.edit_block_prompt import (
	edit_format_system,
	practice_messages,
)
from byte.domain.edit_format.service.edit_block_service import EditBlockService
from byte.domain.edit_format.service.shell_command_prompt import (
	shell_command_system,
	shell_practice_messages,
)
from byte.domain.edit_format.service.shell_command_service import ShellCommandService


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

		if config.edit_format.enable_shell_commands:
			# Combine system prompts to provide AI with both edit and shell capabilities
			combined_system = f"{edit_format_system}\n\n{shell_command_system}"

			# Combine practice messages to show examples of both edit blocks and shell commands
			combined_examples = practice_messages + shell_practice_messages

			self.prompts = EditFormatPrompts(system=combined_system, examples=combined_examples)
		else:
			self.prompts = EditFormatPrompts(system=edit_format_system, examples=practice_messages)

	async def handle(self, content: str) -> List[SearchReplaceBlock]:
		"""Process content by validating, parsing, and applying edit blocks and shell commands.

		First processes all file edit blocks through the complete workflow (validation,
		parsing, application). Then, if shell commands are enabled and all edits succeeded,
		executes any shell command blocks found in the content.

		Args:
			content: Raw content string containing edit instructions and optional shell commands

		Returns:
			List of SearchReplaceBlock objects representing individual edit operations

		Raises:
			PreFlightCheckError: If content contains malformed edit blocks

		Usage: `blocks = await service.handle(ai_response)`
		"""
		config = await self.make(ByteConfg)
		edit_block_service = await self.make(EditBlockService)

		# Process file edit blocks
		blocks = await edit_block_service.handle(content)

		# Only execute shell commands if enabled and all edit blocks succeeded
		if config.edit_format.enable_shell_commands:
			all_edits_valid = all(b.block_status == BlockStatus.VALID for b in blocks)

			if all_edits_valid:
				shell_command_service = await self.make(ShellCommandService)
				await shell_command_service.handle(content)
			else:
				# Log that shell commands were skipped due to failed edits

				log.info("Skipping shell command execution due to failed edit blocks")

		return blocks
