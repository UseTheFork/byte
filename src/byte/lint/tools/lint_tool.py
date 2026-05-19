from pathlib import Path
from typing import override

from byte.lint import LintService
from byte.tools import BaseTool, ToolResult


class LintTool(BaseTool):
    name: str = "lint_files"
    description: str = (
        "Runs the configured linters against all files touched during the current session. "
        "Reads the list of modified file paths, executes lint checks on each, "
        "and returns a structured pass/fail result. If linting is disabled in config the "
        "tool exits immediately with a no-op message. On failure, the full lint error output "
        "is returned."
    )
    input_schema = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    @override
    async def run(
        self,
        state,
        **kwargs,
    ) -> ToolResult:

        lint_service = self.app.make(LintService)

        if not self.app["config"].lint.enable:
            return ToolResult(result={"content": "Linting is disabled"})

        # Extract file paths from parsed blocks
        file_paths = []
        for path in state["touched_files"]:
            file_paths.append(Path(str(path)))

        lint_commands = await lint_service.lint_files(file_paths)

        do_fix, failed_commands = await lint_service.display_results_summary(lint_commands)
        if do_fix:
            joined_lint_errors = lint_service.format_lint_errors(failed_commands)
            return ToolResult(result={"content": f"Linting resulted in the following error:\n\n {joined_lint_errors}"})

        return ToolResult(result={"content": "PASS - No Errors Found"})

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        # Successfully created commit:
        return result.result.get("content", "")
