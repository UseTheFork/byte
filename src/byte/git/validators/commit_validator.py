from typing import cast

from byte.git import CommitGroup, CommitMessage
from byte.orchestration import BaseState, ValidationError, Validator
from byte.support.mixins import UserInteractive
from byte.tui import Messages


class CommitValidator(Validator, UserInteractive):
    """Validator for commit messages and commit plans with user confirmation.

    Validates CommitMessage and CommitPlan objects by displaying formatted
    commit messages to the user and prompting for approval. If rejected,
    returns a ValidationError with the user's requested changes.

    Usage: `validator = app.make(CommitValidator)`
    Usage: `errors = await validator.validate(state)`
    """

    async def _display_commit_message(
        self,
        message_number: int,
        total_number: int,
        content: CommitMessage,
    ):
        if isinstance(content, CommitGroup):
            formatted_content = content.format_with_files()
        else:
            formatted_content = content.format()

        await self.emit_tui(
            Messages.CreatePanel(
                formatted_content,
                title=f"Commit Message ({message_number} / {total_number})",
                border_style="warning",
            )
        )

    async def _validate_commit_message(
        self,
        content: CommitMessage | CommitGroup,
    ) -> list[ValidationError | None]:
        confirmed, change = await self.prompt_for_confirm_or_input("Approve Commit?", "What should be changed?", True)

        if confirmed:
            return [None]

        return [ValidationError(context=content.format(), message=str(change))]

    async def validate(self, state: BaseState) -> list[ValidationError | None]:
        content = state["extracted_content"]

        commit_message = cast(CommitMessage, content)
        await self._display_commit_message(
            1,
            1,
            commit_message,
        )
        return await self._validate_commit_message(commit_message)
