from typing import override

from byte.files import FileMode, FileService
from byte.tools import BaseTool, ToolResult


class AddFilesTool(BaseTool):
    name: str = "add_files"
    description: str = (
        "Add one or more files to the Project State section so their contents become available in context. "
        "Only use this tool with known file paths. Check Project State first to see if the file is already loaded."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "file_paths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of file paths to read (relative to the project root)",
            },
        },
        "required": ["file_paths"],
    }

    @override
    async def run(
        self,
        file_paths: list[str] = [],
        **kwargs,
    ) -> ToolResult:

        file_service = self.app.make(FileService)

        rows = []
        for file_path in file_paths:
            if await file_service.is_file_in_context(file_path):
                rows.append(f"| `{file_path}` | Already in Context |")
                continue

            added = await file_service.add_file(file_path, FileMode.READ_ONLY)
            if added:
                rows.append(f"| `{file_path}` | Loaded |")
            else:
                rows.append(f"| `{file_path}` | Does Not Exist |")

        table = "| File | Status |\n|------|--------|\n" + "\n".join(rows)
        return ToolResult(result={"content": table})

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")
