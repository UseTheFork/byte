from pathlib import Path
from typing import override

from byte.lsp import LSPService
from byte.tools import BaseTool, ToolResult


class GetHoverInfoTool(BaseTool):
    name: str = "get_hover_info"
    description: str = "Get hover information for a symbol at a specific position in a file. Uses the Language Server Protocol to retrieve documentation, type information, and other details about code symbols."
    input_schema = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the file (relative or absolute)",
            },
            "line": {
                "type": "integer",
                "description": "The line number (one-based, as shown in editors)",
            },
            "character": {
                "type": "integer",
                "description": "The character position on the line (zero-based)",
            },
        },
        "required": ["file_path", "line", "character"],
    }

    @override
    async def run(
        self,
        file_path: str = "",
        line: int = 0,
        character: int = 0,
        **kwargs,
    ) -> ToolResult:
        lsp_service = self.app.make(LSPService)

        path_obj = Path(file_path).resolve()

        if not path_obj.exists():
            return ToolResult(result={"content": f"Error: File '{file_path}' does not exist"})

        try:
            hover_result = await lsp_service.get_hover(path_obj, line, character)

            if hover_result:
                return ToolResult(result={"content": hover_result.contents})
            else:
                return ToolResult(
                    result={"content": f"No hover information available at {file_path}:{line}:{character}"}
                )

        except Exception as e:
            return ToolResult(result={"content": f"Error getting hover information: {e!s}"})

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")
