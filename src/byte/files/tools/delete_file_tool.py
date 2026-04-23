from typing import Any, override

from langchain_core.tools import ArgsSchema

from byte import Application
from byte.files import ToolFileService
from byte.tools import BaseTool, ToolResult

delete_file_schema = {
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "description": "The EXACT Path to file located in `<file>`. Use the `source` variable.",
        },
    },
    "required": ["path"],
}


class DeleteFileTool(BaseTool):
    name: str = "DeleteFileTool"
    description: str = "Delete a file."
    args_schema: ArgsSchema | None = delete_file_schema

    @override
    async def _arun(
        self,
        path: str = "",
        **kwargs: Any,
    ) -> ToolResult:
        app: Application = kwargs.get("app")  # ty:ignore[invalid-assignment]

        try:
            tool_file_service = app.make(ToolFileService)
            result = await tool_file_service.delete_file(path)

            return ToolResult(
                result=result,
                extra={
                    "touched_files": [path],
                },
            )

        except Exception as e:
            return ToolResult(
                result=f"Error editing file: {e!s}",
            )
