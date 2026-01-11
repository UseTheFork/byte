from byte.agent import ValidationError
from byte.agent.validators.base import Validator


class MaxLinesValidator(Validator):
    """Validates content doesn't exceed maximum line count."""

    def boot(self, **kwargs):
        # Access max_lines from stored kwargs
        self.max_lines = self.kwargs.get("max_lines", 100)  # default to 100 if not provided

    async def validate(self, content: str) -> list[ValidationError]:
        lines = [line for line in content.split("\n") if line.strip()]
        line_count = len(lines)

        if line_count > self.max_lines:
            return [ValidationError(f"Content exceeds maximum line limit: {line_count} lines (max:{self.max_lines})")]

        return []
