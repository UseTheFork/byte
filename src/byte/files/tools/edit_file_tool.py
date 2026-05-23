from typing import override

from byte.files import ToolFileService
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolRunException


class EditFileTool(BaseTool):
    name: str = "edit_file_tool"
    description: str = """Edit a file by replacing a specific string. The search_string must match exactly character for character.\n\n > **Critical **: The tool is extremely literal. Text must match **EXACTLY**"""
    input_schema = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The EXACT Path to a `editable` file located in `<file>`. Use the `source` variable.",
            },
            "search_string": {"type": "string", "description": "The exact string to find and replace"},
            "replace_string": {"type": "string", "description": "The string to replace with"},
        },
        "required": ["file_path", "search_string", "replace_string"],
    }

    @override
    async def run(
        self,
        file_path: str = "",
        search_string: str = "",
        replace_string: str = "",
        **kwargs,
    ) -> ToolResult:

        try:
            tool_file_service = self.app.make(ToolFileService)

            result = await tool_file_service.edit_file(file_path, search_string, replace_string)

            return ToolResult(
                result={"content": result},
                extra={
                    "touched_files": [file_path],
                },
            )

        except Exception as e:
            raise ToolRunException(f"Error editing file: {e!s}") from e

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")
