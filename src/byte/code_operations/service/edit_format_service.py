from byte import Service
from byte.code_operations import (
    EditFormatPrompts,
    ParserService,
)
from byte.code_operations.service.shell_command_prompt import (
    shell_command_system,
    shell_practice_messages,
)
from byte.support.mixins import UserInteractive


class EditFormatService(Service, UserInteractive):
    """Orchestrates edit format operations including file edits and optional shell commands.

    Combines edit block processing with shell command execution based on configuration.
    When shell commands are enabled, provides unified prompts that include both capabilities.
    Shell commands are only executed after all file edits successfully complete.

    Usage: `blocks = await service.handle(ai_response)`
    """

    def boot(self, **kwargs):
        """Initialize service with appropriate prompts based on configuration."""
        self.edit_block_service = self.app.make(ParserService)

        if self.app["config"].edit_format.enable_shell_commands:
            # Combine system prompts to provide AI with both edit and shell capabilities
            combined_system = f"{self.edit_block_service.prompts.system}\n\n{shell_command_system}"

            # Combine practice messages to show examples of both edit blocks and shell commands
            combined_examples = self.edit_block_service.prompts.examples + shell_practice_messages

            self.prompts = EditFormatPrompts(
                system=combined_system,
                enforcement=self.edit_block_service.prompts.enforcement,
                recovery_steps=self.edit_block_service.prompts.recovery_steps,
                examples=combined_examples,
            )
        else:
            self.prompts = EditFormatPrompts(
                system=self.edit_block_service.prompts.system,
                enforcement=self.edit_block_service.prompts.enforcement,
                recovery_steps=self.edit_block_service.prompts.recovery_steps,
                examples=self.edit_block_service.prompts.examples,
            )
