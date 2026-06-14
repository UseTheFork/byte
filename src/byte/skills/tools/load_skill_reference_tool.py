from typing import override

from byte.skills import SkillLoaderService
from byte.support.string import Str
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolValidationException


class LoadSkillReferenceTool(BaseTool):
    name: str = "load_skill_reference_tool"
    description: str = (
        "Use this tool to load a reference file from a skill. Call this when you want to access additional documentation or resources attached to a skill."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "skill_id": {
                "type": "string",
                "description": "The ID of the skill that contains the reference.",
            },
            "reference_name": {
                "type": "string",
                "description": "The name of the reference file (without the .md extension) to load from the skill.",
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

        normalized_reference_name = Str.normalize_id(reference_name)
        reference_path = skill.references.get(normalized_reference_name)
        if reference_path is None:
            raise ToolValidationException(
                f"Reference '{reference_name}' not found in skill '{skill_id}'."
            )

        try:
            content = reference_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise ToolValidationException(
                f"Could not read reference file '{reference_name}': {exc}"
            ) from exc

        return ToolResult(
            result={
                "skill_id": skill_id,
                "reference_name": reference_name,
                "content": content,
            },
        )

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")

    @classmethod
    def format_tui_message(cls, result: ToolResult) -> str:
        skill_id = result.result.get("skill_id", "")
        reference_name = result.result.get("reference_name", "")
        return f"Reference '{reference_name}' from skill '{skill_id}' loaded."
