from typing import Annotated

from langchain.tools import InjectedToolArg, tool

from byte import Application
from byte.tools import ToolResult


@tool(
    description="Commit staged changes with a structured commit message.",
)
async def git_commit(
    type: Annotated[
        str,
        "The commit type. Refer to the <rules type='Allowed Commit Types'> section for valid types and their descriptions.",
    ],
    scope: Annotated[
        str | None,
        "OPTIONAL scope providing additional contextual information. Refer to the <rules type='Allowed Commit Scopes'> section for valid scope values.",
    ],
    commit_message: Annotated[
        str,
        "The description part of the commit message only (without the type prefix). Refer to the <rules type='Commit Description Guidelines'> section for formatting requirements.",
    ],
    breaking_change: Annotated[bool, "Flag indicating whether this commit introduces a breaking change."],
    breaking_change_message: Annotated[
        str | None,
        "REQUIRED if breaking_change is True AND the commit_message isn't sufficiently informative. Describes the breaking change.",
    ],
    body: Annotated[
        str | None,
        "OPTIONAL body with motivation for the change and contrast with previous behavior. Only needed if the commit_message isn't sufficiently informative. Use imperative, present tense: 'change' not 'changed' nor 'changes'. Should explain why the change was made, not what was changed (code shows that). If breaking_change is True, describe the breaking changes here.",
    ],
    app: Annotated[Application, InjectedToolArg],
) -> ToolResult:
    """Commit staged changes with a structured commit message.

    Args:
        type: The commit type
        scope: Optional scope
        commit_message: The commit description
        breaking_change: Whether this is a breaking change
        breaking_change_message: Description of breaking change if applicable
        body: Optional commit body
        app: Application instance

    Returns:
        ToolResult with commit status
    """
    return ToolResult(result="success")
