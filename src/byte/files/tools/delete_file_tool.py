from typing import override

from byte.files import ToolFileService
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolRunException


class DeleteFileTool(BaseTool):
    name: str = "delete_file"
    description: str = "Delete a file."
    input_schema = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The EXACT Path to file located in `<file>`. Use the `source` variable.",
            },
        },
        "required": ["file_path"],
    }

    @override
    async def run(
        self,
        file_path: str = "",
        **kwargs,
    ) -> ToolResult:

        try:
            tool_file_service = self.app.make(ToolFileService)
            result = await tool_file_service.delete_file(file_path)

            return ToolResult(
                result={"content": result},
                extra={
                    "touched_files": [file_path],
                },
            )

        except Exception as e:
            raise ToolRunException(f"Error deleting file: {e!s}") from e

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")
