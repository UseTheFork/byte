from typing import override

from byte.git import CommitService, GitService
from byte.git.schemas import CommitMessage
from byte.support import MD, Section
from byte.tools import BaseTool, ToolDeclinedException, ToolResult, ToolRunException
from byte.tui import InteractionService, Messages


# TODO: we should have a hook that can modify input_schema on the base tool maybe have it be a static method of the class?
class GitCommitTool(BaseTool):
    name: str = "git_commit"
    description: str = (
        "Create a git commit with the provided commit message details following conventional commit standards."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "description": f"The commit type. Refer to the {Section.sub_heading_ref('Allowed Commit Types')} section for valid types and their descriptions.",
            },
            "commit_message": {
                "type": "string",
                "description": f"The description part of the commit message only (without the type prefix). Refer to the {Section.sub_heading_ref('Commit Description Guidelines')} section for formatting requirements.",
            },
            "scope": {
                "type": "string",
                "description": f"OPTIONAL scope providing additional contextual information. Refer to the {Section.sub_heading_ref('Allowed Commit Scopes')} section for valid scope values.",
            },
            "breaking_change": {
                "type": "boolean",
                "description": "Flag indicating whether this commit introduces a breaking change.",
            },
            "breaking_change_message": {
                "type": "boolean",
                "description": "REQUIRED if breaking_change is True AND the commit_message isn't sufficiently informative. Describes the breaking change.",
            },
            "body": {
                "type": "array",
                "items": {"type": "string"},
                "description": """OPTIONAL list of body lines with motivation for the change and contrast with previous behavior.
                - Only needed if the commit_message isn't sufficiently informative.
                - Use imperative, present tense: 'change' not 'changed' nor 'changes'.
                - Should explain why the change was made, not what was changed (code shows that).
                - If breaking_change is True, describe the breaking changes here.""",
            },
        },
        "required": ["type", "commit_message"],
    }

    @override
    async def run(
        self,
        type: str,
        commit_message: str,
        breaking_change: bool = False,
        scope: str | None = None,
        breaking_change_message: str | None = None,
        body: list[str] | None = None,
        **kwargs,
    ) -> ToolResult:

        git_service = self.app.make(GitService)
        commit_service = self.app.make(CommitService)
        interaction_service = self.app.make(InteractionService)

        commit = CommitMessage(
            type=type,
            scope=scope,
            commit_message=commit_message,
            breaking_change=breaking_change,
            breaking_change_message=breaking_change_message,
            body="\n".join(f"- {line}" for line in body) if body else None,
        )

        formatted_message = commit.format()

        self.app.emit_tui(
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
            raise ToolDeclinedException(
                MD.list_to_text(
                    [
                        "Make the following changes:",
                        str(change),
                    ]
                )
            )

        if confirmed:
            try:
                formatted_message = await commit_service.format_conventional_commit(commit)
                await git_service.commit(formatted_message)

                return ToolResult(result={"content": f"Successfully created commit: {formatted_message}"})

            except Exception as e:
                raise ToolRunException(f"Error creating git commit: {e!s}") from e

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        # Successfully created commit:
        return result.result.get("content", "")
