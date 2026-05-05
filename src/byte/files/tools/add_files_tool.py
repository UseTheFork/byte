from typing import override

from byte.files import FileMode, FileService
from byte.support import Section, SectionType
from byte.support.utils import list_to_multiline_text
from byte.tools import BaseTool, ToolResult


class AddFilesTool(BaseTool):
    name: str = "add_files"
    description: str = list_to_multiline_text(
        [
            f"Add one or more files to the {Section.ref(SectionType.PROJECT_FILES)} section so their contents become available in context.",
            Section.start(SectionType.RULES),
            f" - YOU MUST check the {Section.ref(SectionType.PROJECT_FILES)}",
            " - Only use this tool with known file paths.",
            " - Use only when the file content is not already available in the prompt or known state.",
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
