from typing import Annotated

from langchain.tools import InjectedToolArg, tool

from byte import Application
from byte.git import CommitService, GitService
from byte.git.schemas import CommitMessage
from byte.tui import InteractionService, Messages


@tool(
    extras={"eager_input_streaming": True},
    description="Create a git commit with the provided commit message details following conventional commit standards.",
)
async def git_commit(
    type: Annotated[
        str,
        "The commit type. Refer to the <rules type='Allowed Commit Types'> section for valid types and their descriptions.",
    ],
    commit_message: Annotated[
        str,
        "The description part of the commit message only (without the type prefix). Refer to the <rules type='Commit Description Guidelines'> section for formatting requirements.",
    ],
    scope: Annotated[
        str | None,
        "OPTIONAL scope providing additional contextual information. Refer to the <rules type='Allowed Commit Scopes'> section for valid scope values.",
    ] = None,
    breaking_change: Annotated[bool, "Flag indicating whether this commit introduces a breaking change."] = False,
    breaking_change_message: Annotated[
        str | None,
        "REQUIRED if breaking_change is True AND the commit_message isn't sufficiently informative. Describes the breaking change.",
    ] = None,
    body: Annotated[
        str | None,
        "OPTIONAL body with motivation for the change and contrast with previous behavior. Only needed if the commit_message isn't sufficiently informative.",
    ] = None,
    app: Annotated[Application | None, InjectedToolArg] = None,
) -> str:
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

    confirmed, change = await interaction_service.confirm_or_input("Approve Commit?", "What should be changed?", True)

    if not confirmed:
        return str(change)

    if confirmed:
        try:
            formatted_message = await commit_service.format_conventional_commit(commit)
            await git_service.commit(formatted_message)

            return f"Successfully created commit: {formatted_message}"

        except Exception as e:
            return f"Error creating git commit: {e!s}"

    return "User declined the tool call."
