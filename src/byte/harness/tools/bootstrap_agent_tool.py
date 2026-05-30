from typing import override

from byte.files import FileService
from byte.orchestration import BaseState, HarnessStateUtils
from byte.skills import SkillLoaderService
from byte.support import Section, SectionType
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolValidationException


class BootstrapAgentTool(BaseTool):
    name: str = "bootstrap_tool"
    description: str = (
        "Load skills, editable files, and reference files into the agent harness based on the workflow requirements."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "instruction": {
                "type": "string",
                "description": "A short, clear, concise instruction to pass to the coding agent on exactly what must be done to complete the users task.",
            },
            "skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of skill names to load into the harness.",
            },
            "editable_files": {
                "type": "array",
                "items": {"type": "string"},
                "description": f"List of file paths that can be edited in the current workflow. These are in the {Section.ref(SectionType.PROJECT_FILES)} section under {Section.sub_heading_ref('Editable Files')}. This should NOT include any new files that will be created.",
            },
            "reference_files": {
                "type": "array",
                "items": {"type": "string"},
                "description": f"List of reference file paths to provide context to the agent. These are in the {Section.ref(SectionType.PROJECT_FILES)} section under {Section.sub_heading_ref('Reference Files')}.",
            },
        },
        "required": ["instruction"],
    }

    @override
    async def run(
        self,
        state: BaseState,
        instruction: str,
        skills: list[str] = [],
        editable_files: list[str] = [],
        reference_files: list[str] = [],
        reference_context: list[str] = [],
        **kwargs,
    ) -> ToolResult:
        harness = HarnessStateUtils.get_harness(state)

        skill_loader_service = self.app.make(SkillLoaderService)

        harness["instruction"] = instruction

        invalid = [name for name in skills if skill_loader_service.get_skill(name) is None]
        if invalid:
            raise ToolValidationException(f"Unknown skill(s): {', '.join(invalid)}.")

        harness["skills"] = skills

        file_service = self.app.make(FileService)

        missing_editable = [f for f in editable_files if file_service.get_file_context(f) is None]
        missing_reference = [f for f in reference_files if file_service.get_file_context(f) is None]

        all_missing = missing_editable + missing_reference
        if all_missing:
            raise ToolValidationException(f"File(s) not found: {', '.join(all_missing)}.")

        harness = HarnessStateUtils.set_files(state, edit=editable_files, reference=reference_files)

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
