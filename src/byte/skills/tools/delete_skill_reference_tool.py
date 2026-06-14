from typing import override

from byte.skills import SkillLoaderService
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolValidationException


class DeleteSkillReferenceTool(BaseTool):
    name: str = "delete_skill_reference_tool"
    description: str = "Use this tool to delete a reference from an existing skill."
    input_schema = {
        "type": "object",
        "properties": {
            "skill_id": {
                "type": "string",
                "description": "The ID of the skill to delete the reference from.",
            },
            "reference_name": {
                "type": "string",
                "description": "The name/key of the reference to delete.",
            },
        },
        "required": ["skill_id", "reference_name"],
    }

    @override
    async def run(
        self,
        skill_id: str,
        reference_name: str,
        **kwargs,
    ) -> ToolResult:

        skill_loader_service = self.app.make(SkillLoaderService)
        skill = skill_loader_service.get_skill(skill_id)
        if skill is None:
            raise ToolValidationException(f"Skill '{skill_id}' not found.")

        if reference_name not in skill.references:
            raise ToolValidationException(
                f"Reference '{reference_name}' not found in skill '{skill_id}'."
            )

        reference_file = skill.references[reference_name]
        try:
            reference_file.unlink()
        except (OSError, PermissionError) as exc:
            raise ToolValidationException(f"Could not delete reference file {reference_file}: {exc}")

        skill_loader_service.reload()

        return ToolResult(
            result={
                "skill_id": skill_id,
                "reference_name": reference_name,
                "content": f"Reference '{reference_name}' deleted from skill '{skill_id}'.",
            },
        )

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")

    @classmethod
    def format_tui_message(cls, result: ToolResult) -> str:
        skill_id = result.result.get("skill_id", "")
        reference_name = result.result.get("reference_name", "")
        return f"Reference '{reference_name}' deleted from skill '{skill_id}'."
