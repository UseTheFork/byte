from typing import override

from byte.files import FileService
from byte.orchestration import BaseState
from byte.support import MD, Section, SectionType
from byte.support.utils import list_to_multiline_text
from byte.tools import BaseTool, ToolResult


class AddFilesTool(BaseTool):
    name: str = "add_files_tool"
    description: str = list_to_multiline_text(
        [
            f"Add one or more files to {Section.ref(SectionType.PROJECT_FILES)} for the current workflow.",
            MD.bullet("Only use this tool with known file paths."),
            MD.bullet(f"Use only when the file is NOT already in the {Section.ref(SectionType.PROJECT_FILES)}."),
        ]
    )
    input_schema = {
        "type": "object",
        "properties": {
            "file_paths": {
                "type": "array",
                "items": {"type": "string"},
                "description": f"List of file paths to add to {Section.ref(SectionType.PROJECT_FILES)} (relative to the project root)",
            },
        },
        "required": ["file_paths"],
    }

    @override
    async def run(
        self,
        state: BaseState,
        file_paths: list[str] = [],
        **kwargs,
    ) -> ToolResult:
        harness = state.get("harness", {})
        file_service = self.app.make(FileService)

        missing_files = [f for f in file_paths if file_service.get_file_context(f) is None]
        if missing_files:
            return ToolResult(success=False, result={"content": f"File(s) not found: {', '.join(missing_files)}."})

        current_editable = harness.get("editable_files", [])
        updated_editable = list(set(current_editable + file_paths))

        harness["editable_files"] = updated_editable

        return ToolResult(
            result={"content": f"Added {len(file_paths)} file(s) to= files. Total files: {len(updated_editable)}."},
            extra={"harness": harness},
        )

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")
