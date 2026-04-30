from typing import override

from byte.git import GitService
from byte.support import Boundary, BoundaryType, Section, SectionType
from byte.support.utils import list_to_multiline_text
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolRunException

MAX_RESULT_LENGTH = 10000


class GitGrepTool(BaseTool):
    name: str = "git_grep"
    description: str = list_to_multiline_text(
        [
            "Search for a pattern in tracked files using git grep. This tool searches through all files tracked by git for the specified pattern. It's useful for finding where specific code, functions, or text appears in the codebase.",
            f"BEFORE using this tool you MUST check the provided {Boundary.open(BoundaryType.FILE)} in {Section.ref(SectionType.PROJECT_STATE)}.",
        ]
    )
    input_schema = {
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

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")

    @override
    async def run(
        self,
        pattern: str = "",
        file_pattern: str = "",
        **kwargs,
    ) -> ToolResult:

        git_service = self.app.make(GitService)

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
                    return ToolResult(result={"content": f"No matches found for pattern: {pattern}"})
                if len(result) > MAX_RESULT_LENGTH:
                    result = result[:MAX_RESULT_LENGTH] + "\n... [results truncated]"
                return ToolResult(result={"content": result})
            except Exception as grep_error:
                # Git grep returns non-zero exit code when no matches found
                error_msg = str(grep_error)
                if "did not match any file(s) known to git" in error_msg or "no matches" in error_msg.lower():
                    return ToolResult(result={"content": f"No matches found for pattern: {pattern}"})
                raise

        except Exception as e:
            raise ToolRunException(f"Error executing git grep for pattern '{pattern}': {e!s}") from e
