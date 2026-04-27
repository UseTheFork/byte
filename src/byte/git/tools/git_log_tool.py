from typing import Annotated, Any, Optional, override

from langchain.tools import InjectedToolArg
from langchain_core.tools import ArgsSchema
from pydantic import BaseModel, Field

from byte.git import GitService
from byte.tools import BaseTool, ToolResult


class GitLogToolInput(BaseModel):
    """Input for GitLogTool"""

    max_count: int = Field(default=20, description="Limit the number of commits returned. Defaults to 20.")
    since: Optional[str] = Field(
        description="Show commits more recent than a specific date (e.g., '2 weeks ago', '2024-01-01').",
    )
    until: Optional[str] = Field(
        description="Show commits older than a specific date (e.g., '2024-06-01').",
    )
    file_path: Optional[str] = Field(
        description="Limit the log to commits that affected the specified file or directory path.",
    )
    oneline: bool = Field(
        default=True, description="If true, output each commit as a single line (hash + subject). Defaults to true."
    )
    app: Annotated[Any | None, InjectedToolArg]


class GitLogTool(BaseTool):
    name: str = "GitLogTool"
    description: str = (
        "Retrieve the git commit log with optional filters. "
        "Use max_count to limit results, author/since/until to filter commits, "
        "branch to target a specific ref, and file_path to scope to a specific file or directory."
    )
    args_schema: ArgsSchema = GitLogToolInput

    @override
    async def _arun(
        self,
        max_count: int = 20,
        since: str | None = None,
        until: str | None = None,
        file_path: str | None = None,
        oneline: bool = True,
        **kwargs: Any,
    ) -> ToolResult:
        app = kwargs.get("app")

        if app is None:
            raise RuntimeError("Application instance is required but was not provided")

        git_service = app.make(GitService)

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
            return ToolResult(result=f"Error retrieving git log: {e!s}")
