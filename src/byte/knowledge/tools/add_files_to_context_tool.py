from pathlib import Path
from typing import override

from byte.knowledge import SessionContextModel, SessionContextService
from byte.orchestration import BaseState
from byte.support import MD, Section, SectionType
from byte.support.utils import list_to_multiline_text
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolValidationException


class AddFilesToContextTool(BaseTool):
    name: str = "add_files_to_context_tool"
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
        session_context_service = self.app.make(SessionContextService)

        context_keys = []
        missing_files = []
        for file_path in file_paths:
            # Convert to Path object, resolve relative paths from project root
            file_path = Path(file_path)
            if not file_path.is_absolute():
                file_path = self.app.root_path(str(file_path))

            # Check if file exists
            if not file_path.exists():
                missing_files.append(file_path)
                continue

            if not file_path.is_file():
                missing_files.append(file_path)
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception:
                continue

            context_key = str(file_path.relative_to(self.app["path"]))

            model = self.app.make(SessionContextModel, type="file", key=context_key, content=content)
            session_context_service.add_context(model)
            context_keys.append(context_key)

        if missing_files:
            raise ToolValidationException(f"File(s) not found: {', '.join(missing_files)}.")

        current_editable = harness.get("reference_context", [])
        updated_editable = list(set(current_editable + context_keys))

        harness["reference_context"] = updated_editable

        return ToolResult(
            result={"content": f"Added {len(context_keys)} file(s) to Context."},
            extra={"harness": harness},
        )

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")
