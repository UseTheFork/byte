import re
from typing import override

from byte.skills import SkillLoaderService
from byte.tools import BaseTool, ToolResult


class CreateSkillTool(BaseTool):
    name: str = "create_skill"
    description: str = "Use this tool to create a new skill. Call this when you want to create a reusable skill with a name, description, and instructions."
    input_schema = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The unique name of the skill (used as the directory name and skill identifier).",
                "maxLength": 64,
            },
            "description": {
                "type": "string",
                "description": "A short description of what the skill does.",
                "maxLength": 1024,
            },
            "instructions": {
                "type": "string",
                "description": "The instructions body for the skill (written as markdown after the frontmatter).",
            },
        },
        "required": ["name", "description", "instructions"],
    }

    @override
    async def run(self, name: str, description: str, instructions: str) -> ToolResult:
        # Normalize the skill name: lowercase, replace invalid chars with hyphens,
        # collapse consecutive hyphens, strip leading/trailing hyphens
        name = name.lower()
        name = re.sub(r"[^a-z0-9]+", "-", name)
        name = re.sub(r"-+", "-", name)
        name = name.strip("-")

        skill_file_path = self.app.skills_path(f"{name}/SKILL.md")
        skill_file_path.parent.mkdir(parents=True, exist_ok=True)

        content = f"---\nname: {name}\ndescription: {description}\n---\n\n{instructions}\n"
        skill_file_path.write_text(content, encoding="utf-8")

        skill_loader_service = self.app.make(SkillLoaderService)
        skill_loader_service.reload()

        return ToolResult(result=f"Skill '{name}' created at {skill_file_path}.")
