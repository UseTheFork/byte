from typing import override

from byte.skills import SkillLoaderService
from byte.support import Boundary, BoundaryType, Section, SectionType
from byte.tools import BaseTool, ToolResult


class LoadSkillTool(BaseTool):
    name: str = "load_skill_tool"
    description: str = (
        "Use this tool to load a skill by name. Call this when you want to use one of the available skills."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "skill_name": {
                "type": "string",
                "description": f"The name of the skill to load. This must be from the {Section.ref(SectionType.AVALIABLE_SKILLS)} and is labeled by `{Boundary.open(BoundaryType.NAME)}`",
            },
        },
        "required": ["skill_name"],
    }

    @override
    async def run(
        self,
        skill_name: str,
        **kwargs,
    ) -> ToolResult:

        skill_loader_service = self.app.make(SkillLoaderService)
        skill = skill_loader_service.get_skill(skill_name)
        if skill is None:
            return ToolResult(result={"content": f"Skill '{skill_name}' not found."})

        return ToolResult(
            result={"content": skill.instructions},
        )

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")
