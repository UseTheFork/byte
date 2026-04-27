from typing import override

from byte.files import ToolFileService
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolRunException


class ReplaceFileTool(BaseTool):
    name: str = "replace_file"
    description: str = "Replace all content in a file."
    input_schema = {
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

    @override
    async def run(
        self,
        file_path: str = "",
        content: str = "",
    ) -> ToolResult:

        try:
            tool_file_service = self.app.make(ToolFileService)
            result = await tool_file_service.replace_file(file_path, content)

            return ToolResult(
                result=result,
                extra={
                    "touched_files": [file_path],
                },
            )

        except Exception as e:
            raise ToolRunException(f"Error replacing file: {e!s}") from e
