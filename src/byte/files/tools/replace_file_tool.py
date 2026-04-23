from typing import Any, override

from langchain_core.tools import ArgsSchema

from byte import Application
from byte.files import ToolFileService
from byte.tools import BaseTool, ToolResult

replace_file_schema = {
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "description": "The EXACT Path to file located in `<file>`. Use the `source` variable.",
        },
        "content": {"type": "string", "description": "Content to replace the file with"},
    },
    "required": ["path", "content"],
}


class ReplaceFileTool(BaseTool):
    name: str = "ReplaceFileTool"
    description: str = "Replace all content in a file."
    args_schema: ArgsSchema | None = replace_file_schema

    @override
    async def _arun(
        self,
        path: str = "",
        content: str = "",
        **kwargs: Any,
    ) -> ToolResult:
        app: Application = kwargs.get("app")  # ty:ignore[invalid-assignment]

        try:
            tool_file_service = app.make(ToolFileService)
            result = await tool_file_service.replace_file(path, content)

            return ToolResult(
                result=result,
                extra={
                    "touched_files": [path],
                },
            )

        except Exception as e:
            return ToolResult(
                result=f"Error replacing file: {e!s}",
            )
