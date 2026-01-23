from typing import cast

from byte.agent import BaseState, ValidationError
from byte.agent.validators.base import Validator
from byte.git import CommitGroup, CommitMessage, CommitPlan
from byte.support.mixins import UserInteractive


class CommitValidator(Validator, UserInteractive):
    """Validator for commit messages and commit plans with user confirmation.

    Validates CommitMessage and CommitPlan objects by displaying formatted
    commit messages to the user and prompting for approval. If rejected,
    returns a ValidationError with the user's requested changes.

    Usage: `validator = app.make(CommitValidator)`
    Usage: `errors = await validator.validate(state)`
    """

    async def _validate_commit_message(
        self,
        message_number: int,
        total_number: int,
        content: CommitMessage | CommitGroup,
    ) -> ValidationError | None:
        if isinstance(content, CommitGroup):
            formatted_content = content.format_with_files()
        else:
            formatted_content = content.format()

        self.app["console"].print_panel(
            formatted_content,
            title=f"Commit Message ({message_number} / {total_number})",
        )

        confirmed, change = await self.prompt_for_confirm_or_input("Approve Commit?", "What should be changed?", True)

        if confirmed:
            return None

        return ValidationError(context=content.format(), message=str(change))

    async def _validate_commit_plan(self, content: CommitPlan) -> list[ValidationError | None]:
        validation_errors: list[ValidationError | None] = []

        total_commits = len(content.commits)
        for index, commit_group in enumerate(content.commits, start=1):
            error = await self._validate_commit_message(index, total_commits, commit_group)
            validation_errors.append(error)

        return validation_errors

    async def validate(self, state: BaseState) -> list[ValidationError | None]:
        content = state["extracted_content"]

        if isinstance(content, CommitPlan):
            return await self._validate_commit_plan(content)
        else:
            result = await self._validate_commit_message(
                1,
                1,
                cast(CommitMessage, content),
            )
            return [result]
