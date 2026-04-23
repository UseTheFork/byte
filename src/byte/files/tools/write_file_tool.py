from typing import Any, override

from langchain_core.tools import ArgsSchema

from byte import Application
from byte.files import ToolFileService
from byte.tools import BaseTool, ToolResult

write_file_schema = {
    "type": "object",
    "properties": {
        "path": {"type": "string", "description": "The EXACT Path to the file."},
        "content": {"type": "string", "description": "Content to write to the file"},
    },
    "required": ["path", "content"],
}


class WriteFileTool(BaseTool):
    name: str = "WriteFileTool"
    description: str = "Write content to a file. Creates parent directories if needed."
    args_schema: ArgsSchema | None = write_file_schema

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
            result = await tool_file_service.write_file(path, content)

            return ToolResult(
                result=result,
                extra={
                    "touched_files": [path],
                },
            )

        except Exception as e:
            return ToolResult(
                result=f"Error writing file: {e!s}",
            )
