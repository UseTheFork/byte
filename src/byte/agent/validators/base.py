from abc import ABC, abstractmethod

from pydantic.dataclasses import dataclass

from byte.support.mixins import Bootable


@dataclass
class ValidationError:
    """Validation error with structured information.

        Usage: `ValidationError(message="Too many lines", code="max_lines_exceeded", context={"count":
    150, "max": 100})`
    """

    message: str  # Human-readable error message
    code: str | None = None  # Machine-readable error code (optional)
    context: dict | None = None  # Additional context data (optional)

    def to_string(self) -> str:
        """Format the validation error as a string.

        Usage: `error.to_string()` -> "- Too many lines"
        """
        return f"- {self.message}"


class Validator(ABC, Bootable):
    """Base class for content validators used in ValidationNode.

    Usage: `class MyValidator(Validator): ...`
    """

    @abstractmethod
    async def validate(self, content: str) -> list[ValidationError]:
        """Validate content and return list of error messages.

        Returns:
            Empty list if valid, list of error strings if invalid

        Usage: `errors = await validator.validate(message_content)`
        """
        pass
