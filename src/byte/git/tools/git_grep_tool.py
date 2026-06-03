from typing import override

from byte.git import GitService
from byte.support import Boundary, BoundaryType, Section, SectionType
from byte.support.command_runner import CommandRunner
from byte.support.utils import list_to_multiline_text
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolRunException

MAX_RESULT_LENGTH = 10000
GIT_GREP_MAX_COUNT = 100


class GitGrepTool(BaseTool):
    name: str = "git_grep_tool"
    description: str = list_to_multiline_text(
        [
            "Search for a pattern in tracked files using git grep. This tool searches through all files tracked by git for the specified pattern. It's useful for finding where specific code, functions, or text appears in the codebase.",
            f"BEFORE using this tool you MUST check the provided {Boundary.open(BoundaryType.FILE)} in {Section.ref(SectionType.PROJECT_FILES)}.",
        ]
    )
    input_schema = {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "The search pattern to look for in tracked files (supports regex).",
            },
            "case_sensitive": {
                "type": "boolean",
                "description": "Whether the search is case-sensitive. Default is False (case-insensitive).",
                "default": False,
            },
            "max_count": {
                "type": "integer",
                "description": "Maximum number of matches to return. Default is 100.",
                "default": GIT_GREP_MAX_COUNT,
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
        case_sensitive: bool = False,
        max_count: int = GIT_GREP_MAX_COUNT,
        file_pattern: str = "",
        **kwargs,
    ) -> ToolResult:

        git_service = self.app.make(GitService)

        try:
            repo = await git_service.get_repo()

            # Build git grep command arguments
            grep_args = ["--no-pager", "grep"]

            # Add case-sensitivity flag
            if not case_sensitive:
                grep_args.append("-i")

            # Add regex and other flags
            grep_args.extend(["-E", "-n", "--no-color", "--max-count", str(max_count), "--", pattern])

            # Add file pattern if provided
            if file_pattern:
                grep_args.append(file_pattern)

            # Execute git grep
            try:
                result = await CommandRunner.run("git", *grep_args, cwd=repo.working_dir)
                if not result:
                    return ToolResult(result={"content": "No matches found"})

                # Parse the output and format results
                formatted_result = self._format_grep_results(result, max_count)

                if len(formatted_result) > MAX_RESULT_LENGTH:
                    formatted_result = formatted_result[:MAX_RESULT_LENGTH] + "\n... [results truncated]"

                return ToolResult(result={"content": formatted_result})

            except RuntimeError as grep_error:
                # Git grep returns exit code 1 when no matches found
                error_msg = str(grep_error)
                if "exit code 1" in error_msg:
                    return ToolResult(result={"content": "No matches found"})
                raise

        except Exception as e:
            raise ToolRunException(f"Error executing git grep for pattern '{pattern}': {e!s}") from e

    @staticmethod
    def _format_grep_results(output: str, max_count: int) -> str:
        """Parse git grep output and format it as structured results grouped by file.

        Args:
            output: Raw output from git grep in format "file:line:content"
            max_count: The max count limit used for grep

        Returns:
            Formatted string with results grouped by file.
        """
        lines = output.strip().split("\n")
        truncated = len(lines) >= max_count

        # Dictionary to store matches grouped by file, preserving order
        file_matches: dict[str, list[tuple[int, str]]] = {}
        file_order: list[str] = []
        seen: set[str] = set()

        # Parse each line of output
        for line in lines:
            if not line:
                continue

            # Split on first two colons to get file:line:content
            parts = line.split(":", 2)
            if len(parts) < 3:
                continue

            fname = parts[0]
            try:
                line_num = int(parts[1])
            except ValueError:
                continue

            content = parts[2]

            # Track file order
            if fname not in seen:
                seen.add(fname)
                file_order.append(fname)
                file_matches[fname] = []

            file_matches[fname].append((line_num, content))

        # Build formatted output
        result_parts: list[str] = []

        if truncated:
            result_parts.append(f"Note: The results have been truncated. Only showing first {max_count} results.")

        for fname in file_order:
            matches = file_matches[fname]
            result_parts.append(f"File: {fname}")
            result_parts.append(f"Match lines: {len(matches)}")
            for line_num, content in matches:
                result_parts.append(f"{line_num}|{content}")
            result_parts.append("")

        return "\n".join(result_parts)
