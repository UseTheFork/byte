from typing import override

from byte.skills import SkillLoaderService
from byte.support.string import Str
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolValidationException


class AddSkillReferenceTool(BaseTool):
    name: str = "add_skill_reference_tool"
    description: str = "Use this tool to add or edit a reference file for a skill. Call this when you want to add supporting documentation or resources to a skill."
    input_schema = {
        "type": "object",
        "properties": {
            "skill_id": {
                "type": "string",
                "description": "The ID of the skill to add the reference to.",
            },
            "reference_name": {
                "type": "string",
                "description": "The name/key for the reference file (will be normalized and used as the filename stem).",
                "maxLength": 64,
            },
            "content": {
                "type": "string",
                "description": "The markdown content to write to the reference file.",
            },
        },
        "required": ["skill_id", "reference_name", "content"],
    }

    @override
    async def run(
        self,
        skill_id: str,
        reference_name: str,
        content: str,
        **kwargs,
    ) -> ToolResult:
        skill_loader_service = self.app.make(SkillLoaderService)
        skill = skill_loader_service.get_skill(skill_id)
        if skill is None:
            raise ToolValidationException(f"Skill '{skill_id}' not found.")

        # Normalize the reference name using utility class
        normalized_name = Str.normalize_id(reference_name)

        # Create references directory if needed
        references_dir = skill.path / "references"
        references_dir.mkdir(parents=True, exist_ok=True)

        # Write the content to the reference file
        reference_file_path = references_dir / f"{normalized_name}.md"
        is_new = not reference_file_path.exists()
        reference_file_path.write_text(content, encoding="utf-8")

        # Reload the skill loader to pick up the new/updated reference
        skill_loader_service.reload()

        action = "created" if is_new else "updated"
        return ToolResult(
            result={
                "skill_id": skill_id,
                "reference_name": normalized_name,
                "content": f"Reference '{normalized_name}' {action} for skill '{skill_id}' at {reference_file_path}.",
            },
        )

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")

    @classmethod
    def format_tui_message(cls, result: ToolResult) -> str:
        skill_id = result.result.get("skill_id", "")
        reference_name = result.result.get("reference_name", "")
        return f"Reference '{reference_name}' for skill '{skill_id}' added/updated."
