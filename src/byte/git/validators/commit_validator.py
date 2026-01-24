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

    async def _display_commit_message(
        self,
        message_number: int,
        total_number: int,
        content: CommitMessage | CommitGroup,
    ):
        if isinstance(content, CommitGroup):
            formatted_content = content.format_with_files()
        else:
            formatted_content = content.format()

        self.app["console"].print_panel(
            formatted_content,
            title=f"Commit Message ({message_number} / {total_number})",
        )

    async def _display_commit_plan(self, content: CommitPlan) -> list[ValidationError | None]:
        validation_errors: list[ValidationError | None] = []

        total_commits = len(content.commits)
        for index, commit_group in enumerate(content.commits, start=1):
            await self._display_commit_message(index, total_commits, commit_group)

        return validation_errors

    async def _validate_commit_plan(self, content: CommitPlan) -> list[ValidationError | None]:
        validation_errors: list[ValidationError | None] = []

        confirmed = await self.prompt_for_confirmation("Approve all Commits?")

        if confirmed:
            return [None]

        commit_choices = [f"Commit {i + 1}" for i, commit in enumerate(content.commits)]
        selected_commits = self.app["console"].multiselect(*commit_choices, title="Select which commits to edit")

        if not selected_commits:
            return [None]

        selected_indices = [commit_choices.index(choice) for choice in selected_commits]

        for i in selected_indices:
            commit = content.commits[i]

            # Display the specific commit being edited
            await self._display_commit_message(i + 1, len(content.commits), commit)

            # Prompt for changes to this specific commit
            change_request = await self.prompt_for_input(f"What changes should be made to Commit {i + 1}?")

            if change_request:
                # Format the context based on commit type
                context = commit.format_with_files() if isinstance(commit, CommitGroup) else commit.format()

                validation_errors.append(ValidationError(context=context, message=str(change_request)))

        return validation_errors

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

        if isinstance(content, CommitPlan):
            await self._display_commit_plan(content)
            return await self._validate_commit_plan(content)
        else:
            commit_message = cast(CommitMessage, content)
            await self._display_commit_message(
                1,
                1,
                commit_message,
            )
            return await self._validate_commit_message(commit_message)
