from typing import override

from byte.files import ToolFileService
from byte.orchestration import BaseState, HarnessStateUtils
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolRunException


class WriteFileTool(BaseTool):
    name: str = "write_file_tool"
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
        file_path: str,
        content: str,
        state: BaseState,
        **kwargs,
    ) -> ToolResult:
        try:
            tool_file_service = self.app.make(ToolFileService)
            result = await tool_file_service.write_file(file_path, content)

            current_editable = HarnessStateUtils.get_editable_files(state)
            updated_editable = list(set(current_editable + [file_path]))
            harness = HarnessStateUtils.set_files(state, edit=updated_editable)

            return ToolResult(
                result={"content": result},
                extra={
                    "touched_files": [file_path],
                    "harness": harness,
                },
            )

        except Exception as e:
            raise ToolRunException(f"Error writing file: {e!s}") from e

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")
