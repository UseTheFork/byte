from langchain_core.tools import tool

from byte.context import make
from byte.git import GitService
from byte.tui import InteractionService


@tool(parse_docstring=True)
async def git_grep(pattern: str, file_pattern: str = "") -> str:
    """Search for a pattern in tracked files using git grep.

    This tool searches through all files tracked by git for the specified pattern.
    It's useful for finding where specific code, functions, or text appears in the codebase.

    Args:
        pattern: The search pattern to look for (supports regex)
        file_pattern: Optional file pattern to limit search (e.g., "*.py" for Python files only)

    Returns:
        Search results showing file paths and matching lines, or an error message if the search fails
    """
    git_service = make(GitService)
    interaction_service = make(InteractionService)

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
