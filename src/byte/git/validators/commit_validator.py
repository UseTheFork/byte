from typing import Any

from byte.agent import ValidationError
from byte.agent.validators.base import Validator
from byte.git import CommitMessage, CommitPlan
from byte.support.mixins import UserInteractive


class CommitValidator(Validator, UserInteractive):
    """"""

    def boot(self, **kwargs):
        # Access max_lines from stored kwargs
        self.max_lines = self.kwargs.get("max_lines", 100)  # default to 100 if not provided

    async def _validate_commit_message(self, content: CommitMessage) -> list[ValidationError]:
        lines = [line for line in content.split("\n") if line.strip()]
        line_count = len(lines)

        if line_count > self.max_lines:
            return [ValidationError(f"Content exceeds maximum line limit: {line_count} lines (max:{self.max_lines})")]

        return []

    async def _validate_commit_plan(self, content: CommitPlan) -> list[ValidationError]:
        # TODO: Implement commit plan validation
        return []

    async def validate(self, content: Any) -> list[ValidationError]:
        if isinstance(content, CommitPlan):
            return await self._validate_commit_plan(content)
        else:
            return await self._validate_commit_message(content)
