from typing import override

from byte.files import FileMode, FileService
from byte.support import Section, SectionType
from byte.support.utils import list_to_multiline_text
from byte.tools import BaseTool, ToolResult


class AddFilesTool(BaseTool):
    name: str = "read_files"
    description: str = list_to_multiline_text(
        [
            f"Add one or more files to the {Section.ref(SectionType.PROJECT_FILES)} section so their contents become available in context.",
            Section.start(SectionType.RULES),
            f" - YOU MUST check the {Section.ref(SectionType.PROJECT_FILES)}",
            " - Only use this tool with known file paths.",
            f" - Use only when the file content is NOT already available in the {Section.ref(SectionType.PROJECT_FILES)} or known state.",
            " - DO NOT use this tool to reread files included verbatim in the current message.",
        ]
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

        files: list[dict] = []
        for file_path in file_paths:
            if await file_service.is_file_in_context(file_path):
                files.append({"file": file_path, "status": "Already in Context"})
                continue

            added = await file_service.add_file(file_path, FileMode.READ_ONLY)
            if added:
                files.append({"file": file_path, "status": "Loaded"})
            else:
                files.append({"file": file_path, "status": "Does Not Exist"})

        return ToolResult(result={"files": files})

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        files: list[dict] = result.result.get("files", [])
        lines = [f"- {f['file']}: {f['status']}" for f in files]
        return "Files loaded:\n" + "\n".join(lines)

    @classmethod
    def format_tui_message(cls, result: ToolResult) -> str:
        files: list[dict] = result.result.get("files", [])
        rows = [f"| `{f['file']}` | {f['status']} |" for f in files]
        return "| File | Status |\n|------|--------|\n" + "\n".join(rows)


