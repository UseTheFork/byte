from typing import override

from byte.files import FileMode, FileService
from byte.tools import BaseTool, ToolResult


class ReadFilesTool(BaseTool):
    name: str = "read_files"
    description: str = (
        "Add one or more files to the Project State section so their contents become available in context."
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
        added = []

        for file_path in file_paths:
            if await file_service.add_file(file_path, FileMode.READ_ONLY):
                added.append(file_path)

        if not added:
            return ToolResult(
                result={"content": "No files were added. Files may not exist in the project or are already in context."}
            )

        files_list = "\n".join(f"- `{f}`" for f in added)
        return ToolResult(
            result={"content": f"The following files have been added to the Project State section:\n{files_list}"}
        )

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")
