from pydantic import BaseModel, Field


class CommitGroup(BaseModel):
    commit_message: str = Field(..., description="The commit message for this group of files.")
    files: list[str] = Field(..., description="List of file paths that are part of this commit.")


class CommitPlan(BaseModel):
    commits: list[CommitGroup] = Field(..., description="List of commit groups, each with a message and files.")


class CommitMessage(BaseModel):
    commit_message: str = Field(..., description="A single commit message for all changes.")
