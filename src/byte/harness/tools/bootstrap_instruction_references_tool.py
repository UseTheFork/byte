from typing import override

from byte.files import FileService
from byte.knowledge import SessionContextService
from byte.orchestration import BaseState, HarnessStateUtils
from byte.support import Section, SectionType
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolValidationException


class BootstrapInstructionReferencesTool(BaseTool):
    name: str = "bootstrap_instruction_references_tool"
    description: str = "Load instruction, reference files, and reference materials into the agent harness based on the workflow requirements."
    input_schema = {
        "type": "object",
        "properties": {
            "instruction": {
                "type": "string",
                "description": "A short, clear, concise instruction to pass to the coding agent on exactly what must be done to complete the users task.",
            },
            "reference_files": {
                "type": "array",
                "items": {"type": "string"},
                "description": f"List of reference file paths to provide context to the agent. These are in the {Section.ref(SectionType.PROJECT_FILES)} section under {Section.sub_heading_ref('Reference Files')}.",
            },
            "reference_materials": {
                "type": "array",
                "items": {"type": "string"},
                "description": f"List of session context keys to include as reference materials for the agent. These are in the {Section.ref(SectionType.REFERENCE_MATERIALS)} section.",
            },
        },
        "required": ["instruction"],
    }

    @override
    async def run(
        self,
        state: BaseState,
        instruction: str,
        reference_files: list[str] = [],
        reference_materials: list[str] = [],
        **kwargs,
    ) -> ToolResult:
        harness = HarnessStateUtils.get_harness(state)

        harness["instruction"] = instruction

        file_service = self.app.make(FileService)

        missing_reference = [f for f in reference_files if file_service.get_file_context(f) is None]
        if missing_reference:
            raise ToolValidationException(f"File(s) not found: {', '.join(missing_reference)}.")

        harness = HarnessStateUtils.set_files(state, reference=reference_files)

        session_context_service = self.app.make(SessionContextService)
        missing_materials = [key for key in reference_materials if session_context_service.get_context(key) is None]
        if missing_materials:
            raise ToolValidationException(f"Reference material(s) not found: {', '.join(missing_materials)}.")

        harness["reference_materials"] = reference_materials

        return ToolResult(
            result={"content": "OK", "instruction": instruction},
            extra={"harness": harness},
        )

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")

    @classmethod
    def format_tui_message(cls, result: ToolResult) -> str:
        """Format the tool result for display in the TUI.

        Override this method to customize how a tool's result is presented.
        """
        return result.result.get("instruction", "")
