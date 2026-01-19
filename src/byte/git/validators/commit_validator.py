from typing import cast

from byte.agent import BaseState, ValidationError
from byte.agent.validators.base import Validator
from byte.git import CommitGroup, CommitMessage, CommitPlan
from byte.support.mixins import UserInteractive


class CommitValidator(Validator, UserInteractive):
    """"""

    async def _validate_commit_message(self, content: CommitMessage | CommitGroup) -> ValidationError | None:
        self.app["console"].print_panel(
            f"{content.format()}",
        )

        confirmed, change = await self.prompt_for_confirm_or_input("Approve Commit?", "What should be changed?", True)

        self.app["log"].debug(confirmed)
        self.app["log"].debug(change)

        if confirmed:
            return None

        return ValidationError(context=content.format(), message=str(change))

    async def _validate_commit_plan(self, content: CommitPlan) -> list[ValidationError | None]:
        # TODO: Implement commit plan validation
        return []

    async def validate(self, state: BaseState) -> list[ValidationError | None]:
        content = state["extracted_content"]

        if isinstance(content, CommitPlan):
            return await self._validate_commit_plan(content)
        else:
            result = await self._validate_commit_message(cast(CommitMessage, content))
            return [result]
