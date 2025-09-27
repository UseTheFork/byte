from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, Field, field_validator

if TYPE_CHECKING:
    from byte.domain.files.service.file_service import FileService


class ExecutionContext:
    """Context object for command execution with error tracking."""

    def __init__(self):
        self.errors: list[str] = []
        self.success_count = 0
        self.total_count = 0

    def add_error(self, error: str) -> None:
        """Add an error message to the context."""
        self.errors.append(error)

    def add_success(self) -> None:
        """Mark a successful operation."""
        self.success_count += 1

    def increment_total(self) -> None:
        """Increment total operation count."""
        self.total_count += 1

    @property
    def has_errors(self) -> bool:
        """Check if any errors occurred."""
        return len(self.errors) > 0

    @property
    def all_successful(self) -> bool:
        """Check if all operations were successful."""
        return not self.has_errors and self.success_count == self.total_count


class BaseCommand(BaseModel, ABC):
    """Base class for all agent commands with validation and execution."""

    class Config:
        """Pydantic configuration."""

        validate_assignment = True
        extra = "forbid"  # Prevent extra fields

    @abstractmethod
    async def execute(self, context: ExecutionContext) -> bool:
        """Execute the command and return success status.

        Args:
            context: Execution context for error tracking

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def validate_preconditions(self, file_service: "FileService") -> list[str]:
        """Validate command can be executed, return list of errors.

        Args:
            file_service: File service for context validation

        Returns:
            List of error messages, empty if valid
        """
        pass


class ReplaceTextCommand(BaseCommand):
    """Command to replace text in an existing file.

    Validates that the target file exists, is in editable context,
    and contains the text to be replaced before execution.
    """

    command: Literal["replace_text_in_file"] = Field(default="replace_text_in_file")
    file_path: Path = Field(..., description="Path to the file to modify")
    old_string: str = Field(..., description="Exact text to replace")
    new_string: str = Field(..., description="Replacement text")

    @field_validator("file_path", mode="before")
    @classmethod
    def validate_file_path(cls, v):
        """Convert string paths to Path objects."""
        if not isinstance(v, str | Path):
            raise ValueError("file_path must be a string or Path")
        return Path(v)

    @field_validator("old_string")
    @classmethod
    def validate_old_string(cls, v):
        """Ensure old_string is not empty."""
        if not v or not v.strip():
            raise ValueError("old_string cannot be empty")
        return v

    async def validate_preconditions(self, file_service: "FileService") -> list[str]:
        """Validate that the file exists, is in context, and contains the target text."""
        errors = []

        # Check if file exists and is in context
        if not await file_service.is_file_in_context(str(self.file_path)):
            errors.append(f"File '{self.file_path}' is not in editable context")
            return errors  # No point checking further if not in context

        if not self.file_path.exists():
            errors.append(f"File '{self.file_path}' does not exist")
            return errors  # No point checking content if file doesn't exist

        # Check if old_string exists in file
        try:
            content = self.file_path.read_text(encoding="utf-8")
            if self.old_string not in content:
                errors.append(f"Text to replace not found in '{self.file_path}'")
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            errors.append(f"Could not read file '{self.file_path}': {e}")

        return errors

    async def execute(self, context: ExecutionContext) -> bool:
        """Execute the text replacement."""
        context.increment_total()

        try:
            content = self.file_path.read_text(encoding="utf-8")
            new_content = content.replace(self.old_string, self.new_string)
            self.file_path.write_text(new_content, encoding="utf-8")
            context.add_success()
            return True
        except Exception as e:
            context.add_error(f"Failed to replace text in '{self.file_path}': {e}")
            return False


class AddFileCommand(BaseCommand):
    """Command to create a new file.

    Validates that the target file doesn't exist and the parent
    directory is accessible before creating the file.
    """

    command: Literal["add_file"] = Field(default="add_file")
    file_path: Path = Field(
        ..., description="Path where the new file should be created"
    )
    new_string: str = Field(..., description="Complete content for the new file")

    @field_validator("file_path", mode="before")
    @classmethod
    def validate_file_path(cls, v):
        """Convert string paths to Path objects."""
        return Path(v)

    @field_validator("new_string")
    @classmethod
    def validate_new_string(cls, v):
        """Allow empty files but ensure the field exists."""
        return v if v is not None else ""

    async def validate_preconditions(self, file_service: "FileService") -> list[str]:
        """Validate that the file doesn't exist and parent directory is accessible."""
        errors = []

        if self.file_path.exists():
            errors.append(f"File '{self.file_path}' already exists")

        # Check if parent directory exists or can be created
        parent_dir = self.file_path.parent
        if not parent_dir.exists():
            try:
                # Try to create parent directories
                parent_dir.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError) as e:
                errors.append(f"Cannot create parent directory '{parent_dir}': {e}")

        return errors

    async def execute(self, context: ExecutionContext) -> bool:
        """Execute the file creation."""
        context.increment_total()

        try:
            # Ensure parent directory exists
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self.file_path.write_text(self.new_string, encoding="utf-8")
            context.add_success()
            return True
        except Exception as e:
            context.add_error(f"Failed to create file '{self.file_path}': {e}")
            return False
