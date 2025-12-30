from pydantic import BaseModel, Field

from byte.domain.agent.implementations.commit.constants import COMMIT_TYPE_LIST


class CommitMessage(BaseModel):
    type: str = Field(
        ...,
        description=f"The commit type. Must be one of: {COMMIT_TYPE_LIST}",
    )
    scope: str | None = Field(
        None,
        description="Optional scope providing additional contextual information (e.g., 'parser', 'api', 'ui').",
    )
    commit_message: str = Field(
        ...,
        description="The description part of the commit message only (without the type prefix). "
        "Must be in imperative mood (e.g., 'add feature' not 'added feature') and not exceed 72 characters.",
    )
    breaking_change: bool = Field(
        False,
        description="Flag indicating whether this commit introduces a breaking change.",
    )
    body: str | None = Field(
        None,
        description="OPTIONAL body with motivation for the change and contrast with previous behavior. "
        "Use imperative, present tense: 'change' not 'changed' nor 'changes'. "
        "Should explain why the change was made, not what was changed (code shows that). "
        "If breaking_change is True, describe the breaking changes here.",
    )


class CommitGroup(CommitMessage):
    files: list[str] = Field(..., description="List of file paths that are part of this commit.")


class CommitPlan(BaseModel):
    commits: list[CommitGroup] = Field(..., description="List of commit groups, each with a message and files.")
