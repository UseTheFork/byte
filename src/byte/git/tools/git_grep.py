from typing import Annotated

from langchain.tools import InjectedToolArg, tool

from byte import Application
from byte.git import GitService
from byte.support import Boundary, BoundaryType
from byte.support.utils import list_to_multiline_text
from byte.tui import InteractionService


@tool(
    extras={"eager_input_streaming": True},
    description=list_to_multiline_text(
        [
            "Search for a pattern in tracked files using git grep. This tool searches through all files tracked by git for the specified pattern. It's useful for finding where specific code, functions, or text appears in the codebase.",
            Boundary.important(
                f"BEFORE using this tool you MUST check the provided {Boundary.open(BoundaryType.FILE)} in {Boundary.open(BoundaryType.CONTEXT)}."
            ),
        ]
    ),
)
async def git_grep(
    pattern: Annotated[str, "The search pattern to look for (supports regex)"],
    file_pattern: Annotated[str, "Optional file pattern to limit search (e.g., '*.py' for Python files only)"] = "",
    app: Annotated[Application | None, InjectedToolArg] = None,
) -> str:
    if app is None:
        raise RuntimeError("Application instance is required but was not provided")

    git_service = app.make(GitService)
    interaction_service = app.make(InteractionService)

    file_pattern_msg = f" in files matching '{file_pattern}'" if file_pattern else " in all tracked files"
    if await interaction_service.confirm(
        f"Search for pattern '{pattern}'{file_pattern_msg}?",
        True,
    ):
        try:
            repo = await git_service.get_repo()

            # Build git grep command arguments
            grep_args = ["-n", "--heading", "--break", pattern]

            # Add file pattern if provided
            if file_pattern:
                grep_args.append("--")
                grep_args.append(file_pattern)

            # Execute git grep
            try:
                result = repo.git.grep(*grep_args)
                return result or f"No matches found for pattern: {pattern}"
            except Exception as grep_error:
                # Git grep returns non-zero exit code when no matches found
                error_msg = str(grep_error)
                if "did not match any file(s) known to git" in error_msg or "no matches" in error_msg.lower():
                    return f"No matches found for pattern: {pattern}"
                raise

        except Exception as e:
            return f"Error executing git grep for pattern '{pattern}': {e!s}"

    return "User declined the tool call."
