from typing import List

from byte.domain.agent.coder.commands import BaseCommand
from byte.domain.files.service.file_service import FileService


class CommandValidator:
    """Validates parsed Pydantic command models before execution.

    Leverages Pydantic's built-in validation for type safety and field validation,
    then adds domain-specific validation for file operations and context checking.
    """

    def __init__(self, file_service: FileService):
        self.file_service = file_service

    async def validate_command(self, command: BaseCommand) -> List[str]:
        """Validate a single command using its built-in validation method.

        Args:
            command: The Pydantic command model to validate

        Returns:
            List of error messages, empty if valid
        """
        # Pydantic validation happens at model creation time
        # Here we just run domain-specific precondition validation
        return await command.validate_preconditions(self.file_service)

    async def validate_commands(self, commands: List[BaseCommand]) -> List[str]:
        """Validate multiple commands and return all errors.

        Args:
            commands: List of Pydantic command models to validate

        Returns:
            List of all error messages across all commands
        """
        all_errors = []
        for i, command in enumerate(commands):
            errors = await self.validate_command(command)
            for error in errors:
                all_errors.append(f"Command {i + 1}: {error}")
        return all_errors
