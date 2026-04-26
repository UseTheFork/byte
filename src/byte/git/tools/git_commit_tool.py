from typing import Any, override

from langchain_core.tools import ArgsSchema

from byte.git import CommitService, GitService
from byte.git.schemas import CommitMessage
from byte.tools import BaseTool, ToolResult
from byte.tui import InteractionService, Messages

git_commit_schema = {
    "type": "object",
    "properties": {
        "type": {
            "type": "string",
            "description": "The commit type. Refer to the <rules type='Allowed Commit Types'> section for valid types and their descriptions.",
        },
        "commit_message": {
            "type": "string",
            "description": "The description part of the commit message only (without the type prefix). Refer to the <rules type='Commit Description Guidelines'> section for formatting requirements.",
        },
        "scope": {
            "type": "string",
            "description": "OPTIONAL scope providing additional contextual information. Refer to the <rules type='Allowed Commit Scopes'> section for valid scope values.",
        },
        "breaking_change": {
            "type": "boolean",
            "description": "Flag indicating whether this commit introduces a breaking change.",
            "default": False,
        },
        "breaking_change_message": {
            "type": "string",
            "description": "REQUIRED if breaking_change is True AND the commit_message isn't sufficiently informative. Describes the breaking change.",
        },
        "body": {
            "type": "string",
            "description": "OPTIONAL body with motivation for the change and contrast with previous behavior. Only needed if the commit_message isn't sufficiently informative.",
        },
    },
    "required": ["type", "commit_message"],
}


class GitCommitTool(BaseTool):
    name: str = "GitCommitTool"
    description: str = (
        "Create a git commit with the provided commit message details following conventional commit standards."
    )
    args_schema: ArgsSchema = git_commit_schema

    @override
    async def _arun(
        self,
        type: str = "",
        commit_message: str = "",
        scope: str | None = None,
        breaking_change: bool = False,
        breaking_change_message: str | None = None,
        body: str | None = None,
        **kwargs: Any,
    ) -> ToolResult:
        app = kwargs.get("app")

        if app is None:
            raise RuntimeError("Application instance is required but was not provided")

        git_service = app.make(GitService)
        commit_service = app.make(CommitService)
        interaction_service = app.make(InteractionService)

        commit = CommitMessage(
            type=type,
            scope=scope,
            commit_message=commit_message,
            breaking_change=breaking_change,
            breaking_change_message=breaking_change_message,
            body=body,
        )

        formatted_message = commit.format()

        app.emit_tui(
            Messages.CreatePanel(
                formatted_message,
                title="Commit Message",
                border_style="warning",
            )
        )

        confirmed, change = await interaction_service.confirm_or_input(
            "Approve Commit?", "What should be changed?", True
        )

        if not confirmed:
            return ToolResult(result=str(change))

        if confirmed:
            try:
                formatted_message = await commit_service.format_conventional_commit(commit)
                await git_service.commit(formatted_message)

                return ToolResult(result=f"Successfully created commit: {formatted_message}")

            except Exception as e:
                return ToolResult(result=f"Error creating git commit: {e!s}")

        return ToolResult(result="User declined the tool call.")
