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
        **kwargs,
    ) -> ToolResult:

        file_service = self.app.make(FileService)
        project_files = await file_service.get_project_files()

        if path:
            normalized = path.rstrip("/")
            prefix = normalized + "/"
            entries: set[str] = set()
            for f in project_files:
                if f == normalized:
                    entries.add(f)
                elif f.startswith(prefix):
                    remainder = f[len(prefix) :]
                    # Only the immediate child (file or first directory segment)
                    top = remainder.split("/")[0]
                    if "/" in remainder:
                        entries.add(prefix + top + "/")
                    else:
                        entries.add(prefix + top)
            filtered = sorted(entries)
        else:
            entries = set()
            for f in project_files:
                top = f.split("/")[0]
                if "/" in f:
                    entries.add(top + "/")
                else:
                    entries.add(top)
            filtered = sorted(entries)

        if not filtered:
            result = "No files found."
        else:
            result = "\n".join(f"- {f}" for f in filtered)

        return ToolResult(result={"content": result})

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")

    @classmethod
    def format_tui_message(cls, result: ToolResult) -> str:
        content = result.result.get("content", "")
        lines = content.splitlines()
        max_lines = 20
        if len(lines) > max_lines:
            truncated = lines[:max_lines]
            truncated.append(f"... ({len(lines) - max_lines} more)")
            return "\n".join(truncated)
        return content
