from typing import override

from byte.orchestration import BaseState
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
        state: BaseState,
        **kwargs,
    ) -> ToolResult:

        harness = state["harness"]

        skill_loader_service = self.app.make(SkillLoaderService)
        skill = skill_loader_service.get_skill(skill_name)
        if skill is None:
            return ToolResult(result={"content": f"Skill '{skill_name}' not found."})

        updated_skills = list(dict.fromkeys([*(harness.get("skills") or []), skill_name]))
        updated_harness = {**harness, "skills": updated_skills}

        return ToolResult(
            result={"content": f"Skill '{skill_name}' loaded."},
            extra={
                "harness": updated_harness,
            },
        )

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")
