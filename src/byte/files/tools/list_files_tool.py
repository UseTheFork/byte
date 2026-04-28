from typing import Optional, override

from byte.files import FileService
from byte.tools import BaseTool, ToolResult


class ListFilesTool(BaseTool):
    name: str = "list_files"
    description: str = "List files in the project. Optionally provide a path to list files in a specific directory; without a path, lists files at the project root."
    input_schema = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Optional directory path to list files in (relative to project root). If not provided, lists files at the project root.",
            },
        },
        "required": [],
    }

    @override
    async def run(
        self,
        path: Optional[str] = None,
    ) -> ToolResult:

        file_service = self.app.make(FileService)
        project_files = await file_service.get_project_files()

        if path:
            # normalized the path to not have a trailing slash
            normalized = path.rstrip("/")
            filtered = [f for f in project_files if f.startswith(normalized + "/") or f == normalized]
        else:
            filtered = project_files

        if not filtered:
            result = "No files found."
        else:
            result = "\n".join(filtered)

        return ToolResult(result=result)
