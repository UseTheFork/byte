from typing import override

from byte.skills import SkillLoaderService
from byte.support import Boundary, BoundaryType, Section, SectionType
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolValidationException


class LoadSkillTool(BaseTool):
    name: str = "load_skill_tool"
    description: str = (
        "Use this tool to load a skill by name. Call this when you want to use one of the available skills."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "skill_id": {
                "type": "string",
                "description": f"The ID of the skill to load. This must be from the {Section.ref(SectionType.AVALIABLE_SKILLS)} and is labeled by `{Boundary.open(BoundaryType.ID)}`",
            },
        },
        "required": ["skill_id"],
    }

    @override
    async def run(
        self,
        skill_id: str,
        **kwargs,
    ) -> ToolResult:

        skill_loader_service = self.app.make(SkillLoaderService)
        skill = skill_loader_service.get_skill(skill_id)
        if skill is None:
            raise ToolValidationException(f"Skill '{skill_id}' not found.")

        return ToolResult(
            result={
                "skill_id": skill_id,
                "content": skill.to_markdown(),
            },
        )

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        content = result.result.get("content", "")
        return content

    @classmethod
    def format_tui_message(cls, result: ToolResult) -> str:
        skill_id = result.result.get("skill_id", "")
        return f"Skill '{skill_id}' loaded."
