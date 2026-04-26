from typing import override

from langchain_core.tools import ArgsSchema

from byte import Application
from byte.files import ToolFileService
from byte.tools import BaseTool, ToolResult

edit_file_schema = {
    "type": "object",
    "properties": {
        "file_path": {
            "type": "string",
            "description": "The EXACT Path to a `editable` file located in `<file>`. Use the `source` variable.",
        },
        "old_string": {"type": "string", "description": "The exact string to find and replace"},
        "new_string": {"type": "string", "description": "The string to replace with"},
    },
    "required": ["file_path", "old_string", "new_string"],
}


class EditFileTool(BaseTool):
    name: str = "EditFileTool"
    description: str = """Edit a file by replacing a specific string. The old_string must match exactly character for character.
    
# Critical Requirements
EXACT MATCHING: The tool is extremely literal. Text must match **EXACTLY**

- Every space and tab character
- Every blank line
- Every newline character
- Indentation level (count the spaces/tabs)
- Comment spacing (`// comment` vs `//comment`)
- Brace positioning (`func() {` vs `func(){`)

UNIQUENESS: old_string MUST uniquely identify target instance

- Include 3-5 lines context BEFORE and AFTER change point
- Include exact whitespace, indentation, surrounding code
- If text appears multiple times, add more context to make it unique
"""
    args_schema: ArgsSchema = edit_file_schema

    @override
    async def _arun(
        self,
        app: Application,
        file_path: str = "",
        old_string: str = "",
        new_string: str = "",
    ) -> ToolResult:

        try:
            tool_file_service = app.make(ToolFileService)

            result = await tool_file_service.edit_file(file_path, old_string, new_string)

            return ToolResult(
                result=result,
                extra={
                    "touched_files": [file_path],
                },
            )

        except Exception as e:
            return ToolResult(
                success=False,
                result=f"Error editing file: {e!s}",
            )
