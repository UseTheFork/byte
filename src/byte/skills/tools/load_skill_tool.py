from typing import override

from byte.skills import SkillTrackerService
from byte.tools import BaseTool, ToolResult


class LoadSkillTool(BaseTool):
    name: str = "load_skill"
    description: str = (
        "Use this tool to load a skill by name. Call this when you want to use one of the available skills."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "skill_name": {
                "type": "string",
                "description": "The name of the skill to mark as loaded.",
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
        skill_tracker_service = self.app.make(SkillTrackerService)
        loaded = skill_tracker_service.mark_loaded(skill_name)
        content = f"Skill '{skill_name}' loaded." if loaded else f"Skill '{skill_name}' not found."
        return ToolResult(result={"content": content})

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")
