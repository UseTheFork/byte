from typing import override

from byte.git import GitService
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolRunException


class GitLogTool(BaseTool):
    name: str = "git_log"
    description: str = (
        "Retrieve the git commit log with optional filters. "
        "Use max_count to limit results, author/since/until to filter commits, "
        "branch to target a specific ref, and file_path to scope to a specific file or directory."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "max_count": {
                "type": "integer",
                "description": "Limit the number of commits returned. Defaults to 20.",
                "default": 20,
            },
            "since": {
                "type": "string",
                "description": "Show commits more recent than a specific date (e.g., '2 weeks ago', '2024-01-01').",
            },
            "until": {
                "type": "string",
                "description": "Show commits older than a specific date (e.g., '2024-06-01').",
            },
            "file_path": {
                "type": "string",
                "description": "Limit the log to commits that affected the specified file or directory path.",
            },
            "oneline": {
                "type": "boolean",
                "description": "If true, output each commit as a single line (hash + subject). Defaults to true.",
                "default": True,
            },
        },
        "required": [],
    }

    @override
    async def run(
        self,
        max_count: int = 20,
        since: str | None = None,
        until: str | None = None,
        file_path: str | None = None,
        oneline: bool = True,
    ) -> ToolResult:

        git_service = self.app.make(GitService)

        try:
            repo = await git_service.get_repo()

            log_args = [f"--max-count={max_count}"]

            if oneline:
                log_args.append("--oneline")

            if since:
                log_args.append(f"--since={since}")

            if until:
                log_args.append(f"--until={until}")

            if file_path:
                log_args.append("--")
                log_args.append(file_path)

            result = repo.git.log(*log_args)

            return ToolResult(result=result or "No commits found matching the given criteria.")

        except Exception as e:
            raise ToolRunException(f"Error retrieving git log: {e!s}") from e
