from typing import override

from langchain_core.tools import ArgsSchema

from byte.git import GitService
from byte.support import Boundary, BoundaryType, Section, SectionType
from byte.support.utils import list_to_multiline_text
from byte.tools import BaseTool, ToolResult
from byte.tui import InteractionService

git_grep_schema = {
    "type": "object",
    "properties": {
        "pattern": {
            "type": "string",
            "description": "The search pattern to look for in tracked files (supports regex).",
        },
        "file_pattern": {
            "type": "string",
            "description": "Optional glob pattern to limit the search to specific files (e.g., '*.py' for Python files only).",
        },
    },
    "required": ["pattern"],
}


MAX_RESULT_LENGTH = 10000


class GitGrepTool(BaseTool):
    name: str = "GitGrepTool"
    description: str = list_to_multiline_text(
        [
            "Search for a pattern in tracked files using git grep. This tool searches through all files tracked by git for the specified pattern. It's useful for finding where specific code, functions, or text appears in the codebase.",
            f"BEFORE using this tool you MUST check the provided {Boundary.open(BoundaryType.FILE)} in {Section.ref(SectionType.PROJECT_STATE)}.",
        ]
    )
    args_schema: ArgsSchema = git_grep_schema

    @override
    async def _arun(
        self,
        pattern: str = "",
        file_pattern: str = "",
        app=None,
    ) -> ToolResult:
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
                    if not result:
                        return ToolResult(result=f"No matches found for pattern: {pattern}")
                    if len(result) > MAX_RESULT_LENGTH:
                        result = result[:MAX_RESULT_LENGTH] + "\n... [results truncated]"
                    return ToolResult(result=result)
                except Exception as grep_error:
                    # Git grep returns non-zero exit code when no matches found
                    error_msg = str(grep_error)
                    if "did not match any file(s) known to git" in error_msg or "no matches" in error_msg.lower():
                        return ToolResult(result=f"No matches found for pattern: {pattern}")
                    raise

            except Exception as e:
                return ToolResult(result=f"Error executing git grep for pattern '{pattern}': {e!s}")

        return ToolResult(result="User declined the tool call.")
