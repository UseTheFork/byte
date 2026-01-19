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

    def format(self) -> str:
        """Format the commit message according to conventional commit standards.

        Creates a formatted commit message string from the model's attributes:
        <type>[optional scope][!]: <description>

        [optional body]

        [optional breaking change footer]

        Usage: `formatted_msg = commit_message.format()`
        """
        header_parts = [self.type]

        if self.scope:
            header_parts.append(f"({self.scope})")

        description = self.commit_message
        description = description[0].lower() + description[1:] if description else description
        description = description.rstrip(".")

        message_parts = []
        breaking_change_footer = None

        if self.breaking_change:
            header_parts.append("!")

            if self.breaking_change_message:
                breaking_change_footer = f"BREAKING CHANGE: {self.breaking_change_message}"

        header = "".join(header_parts) + f": {description}"
        message_parts.append(header)

        if self.body:
            message_parts.extend(["", self.body])

        if breaking_change_footer:
            message_parts.extend(["", breaking_change_footer])

        return "\n".join(message_parts)


class CommitGroup(CommitMessage):
    files: list[str] = Field(..., description="List of file paths that are part of this commit.")

    def format_with_files(self) -> str:
        """Format the commit message with the list of files included.

        Creates a formatted commit message string with files listed below:
        <type>[optional scope][!]: <description>

        [optional body]

        [optional breaking change footer]

        Files:
        - file1.py
        - file2.py

        Usage: `formatted_msg = commit_group.format_with_files()`
        """
        message = self.format()

        if self.files:
            files_list = "\n".join(f"- {file}" for file in self.files)
            message += f"\n\nFiles:\n{files_list}"

        return message


class CommitPlan(BaseModel):
    commits: list[CommitGroup] = Field(..., description="List of commit groups, each with a message and files.")
