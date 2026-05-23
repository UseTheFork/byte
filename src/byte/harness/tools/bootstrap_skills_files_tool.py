from typing import override

from byte.files import FileService
from byte.orchestration import BaseState
from byte.skills import SkillLoaderService
from byte.support import Section, SectionType
from byte.tools import BaseTool, ToolResult


class BootstrapSkillsAndFilesTool(BaseTool):
    name: str = "bootstrap_skills_and_files_tool"
    description: str = (
        "Load skills, editable files, and reference files into the agent harness based on the workflow requirements."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of skill names to load into the harness.",
            },
            "editable_files": {
                "type": "array",
                "items": {"type": "string"},
                "description": f"List of file paths that can be edited in the current workflow. These are in the {Section.ref(SectionType.PROJECT_FILES)} section under {Section.sub_heading_ref('Editable Files')}.",
            },
            "reference_files": {
                "type": "array",
                "items": {"type": "string"},
                "description": f"List of reference file paths to provide context to the agent. These are in the {Section.ref(SectionType.PROJECT_FILES)} section under {Section.sub_heading_ref('Reference Files')}.",
            },
        },
        "required": [],
    }

    @override
    async def run(
        self,
        state: BaseState,
        skills: list[str] = [],
        editable_files: list[str] = [],
        reference_files: list[str] = [],
        **kwargs,
    ) -> ToolResult:
        harness = state.get("harness", {})

        skill_loader_service = self.app.make(SkillLoaderService)

        invalid = [name for name in skills if skill_loader_service.get_skill(name) is None]
        if invalid:
            return ToolResult(
                success=False, result={"content": f"Unknown skill(s): {', '.join(invalid)}. No changes made."}
            )

        harness["skills"] = skills

        file_service = self.app.make(FileService)

        missing_editable = [f for f in editable_files if file_service.get_file_context(f) is None]
        missing_reference = [f for f in reference_files if file_service.get_file_context(f) is None]

        all_missing = missing_editable + missing_reference
        if all_missing:
            return ToolResult(
                success=False, result={"content": f"File(s) not found: {', '.join(all_missing)}. No changes made."}
            )

        harness["editable_files"] = editable_files
        harness["reference_files"] = reference_files

        return ToolResult(
            result={
                "content": f"Harness skills set to: {', '.join(skills)}. Loaded {len(editable_files)} editable file(s) and {len(reference_files)} reference file(s)."
            },
            extra={"harness": harness},
        )

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")
