from pydantic import BaseModel, Field


class CommitMessage(BaseModel):
    type: str = Field(
        ...,
        description="The commit type. Refer to the <rules type='Allowed Commit Types'> section for valid types and their descriptions.",
    )
    scope: str | None = Field(
        None,
        description="OPTIONAL scope providing additional contextual information. Refer to the <rules type='Allowed Commit Scopes'> section for valid scope values.",
    )
    commit_message: str = Field(
        ...,
        description="The description part of the commit message only (without the type prefix). "
        "Refer to the <rules type='Commit Description Guidelines'> section for formatting requirements.",
    )
    breaking_change: bool = Field(
        False,
        description="Flag indicating whether this commit introduces a breaking change.",
    )
    breaking_change_message: str | None = Field(
        None,
        description="REQUIRED if breaking_change is True AND the commit_message isn't sufficiently informative. "
        "Describes the breaking change.",
    )
    body: str | None = Field(
        None,
        description="OPTIONAL body with motivation for the change and contrast with previous behavior. "
        "Only needed if the commit_message isn't sufficiently informative. "
        "Use imperative, present tense: 'change' not 'changed' nor 'changes'. "
        "Should explain why the change was made, not what was changed (code shows that). "
        "If breaking_change is True, describe the breaking changes here.",
    )


class CommitGroup(CommitMessage):
    files: list[str] = Field(..., description="List of file paths that are part of this commit.")


class CommitPlan(BaseModel):
    commits: list[CommitGroup] = Field(..., description="List of commit groups, each with a message and files.")
