from abc import ABC, abstractmethod

from pydantic.dataclasses import dataclass

from byte.agent import BaseState
from byte.prompt_format import Boundary, BoundaryType
from byte.support.mixins import Bootable
from byte.support.utils import list_to_multiline_text


@dataclass
class ValidationError:
    """Validation error with structured information.

        Usage: `ValidationError(message="Too many lines", code="max_lines_exceeded", context={"count":
    150, "max": 100})`
    """

    message: str  # Human-readable error message
    context: str | None = None  # context data for the error message

    def format(self) -> str:
        """Format the validation error as a string.

        Usage: `error.format()`
        """

        return list_to_multiline_text(
            [
                Boundary.open(BoundaryType.ERROR),
                "The following error occurred:",
                f"{self.message}",
                "",
                "```",
                f"{self.context}",
                "```",
                Boundary.close(BoundaryType.ERROR),
            ]
        )


class Validator(ABC, Bootable):
    """Base class for content validators used in ValidationNode.

    Usage: `class MyValidator(Validator): ...`
    """

    @abstractmethod
    async def validate(self, state: BaseState) -> list[ValidationError | None]:
        """Validate content and return list of error messages.

        Returns:
            Empty list if valid, list of error strings if invalid

        Usage: `errors = await validator.validate(message_content)`
        """
        pass
