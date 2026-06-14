from typing import override

from byte.skills import SkillLoaderService
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolValidationException
from byte.tui import InteractionService


class PresentSkillTool(BaseTool):
    name: str = "present_skill_tool"
    description: str = "Present the completed skill to the user for review or feedback."
    input_schema = {
        "type": "object",
        "properties": {
            "skill_id": {
                "type": "string",
                "description": "The ID of the skill to present for review.",
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

        interaction_service = self.app.make(InteractionService)

        confirm_message = f"Skill '{skill_id}' is at: {skill.skill_file_path}\nPlease review. Are you satisfied with the skill?"
        input_message = "Please provide your feedback:"

        confirmed, text_input = await interaction_service.confirm_or_input(
            confirm_message, input_message
        )

        if confirmed:
            return ToolResult(result={"content": "User approved the skill.", "approved": True})

        return ToolResult(result={"content": f"User provided feedback: {text_input.value}", "approved": False})

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")

    @classmethod
    def format_tui_message(cls, result: ToolResult) -> str:
        approved = result.result.get("approved", False)
        if approved:
            return "Skill approved by user."
        return "User provided feedback on skill."
