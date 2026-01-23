from byte.agent import BaseState, ValidationError
from byte.agent.validators.base import Validator
from byte.support.utils import extract_content_from_message, get_last_message


class MaxLinesValidator(Validator):
    """Validates content doesn't exceed maximum line count."""

    def boot(self, max_lines=100, **kwargs):
        # Access max_lines from stored kwargs
        self.max_lines = max_lines  # default to 100 if not provided

    async def validate(self, state: BaseState) -> list[ValidationError | None]:
        last_message = get_last_message(state["scratch_messages"])
        message_content = extract_content_from_message(last_message)

        lines = [line for line in message_content.split("\n") if line.strip()]
        line_count = len(lines)

        if line_count > self.max_lines:
            return [ValidationError(f"Content exceeds maximum line limit: {line_count} lines (max:{self.max_lines})")]

        return []
