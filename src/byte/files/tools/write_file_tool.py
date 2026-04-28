from typing import override

from byte.files import ToolFileService
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolRunException


class WriteFileTool(BaseTool):
    name: str = "write_file"
    description: str = "Write content to a file. Creates parent directories if needed."
    input_schema = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "The EXACT Path to the file."},
            "content": {"type": "string", "description": "Content to write to the file"},
        },
        "required": ["file_path", "content"],
    }

    @override
    async def run(
        self,
        file_path: str = "",
        content: str = "",
    ) -> ToolResult:

        try:
            tool_file_service = self.app.make(ToolFileService)
            result = await tool_file_service.write_file(file_path, content)

            return ToolResult(
                result=result,
                extra={
                    "touched_files": [file_path],
                },
            )

        except Exception as e:
            raise ToolRunException(f"Error writing file: {e!s}") from e
