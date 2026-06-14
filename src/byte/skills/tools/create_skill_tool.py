from typing import override

from byte.skills import SkillLoaderService
from byte.support.string import Str
from byte.support.yaml import Yaml
from byte.tools import BaseTool, ToolResult


class CreateSkillTool(BaseTool):
    name: str = "create_skill_tool"
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
    async def run(
        self,
        name: str,
        description: str,
        instructions: str,
        **kwargs,
    ) -> ToolResult:
        # Normalize the skill name using utility class
        name = Str.normalize_id(name)

        skill_file_path = self.app.skills_path(f"{name}/SKILL.md")
        skill_file_path.parent.mkdir(parents=True, exist_ok=True)

        content = Yaml.render_frontmatter({"name": name, "description": description}, instructions)
        skill_file_path.write_text(content, encoding="utf-8")

        skill_loader_service = self.app.make(SkillLoaderService)
        skill_loader_service.reload()

        return ToolResult(result={"content": f"Skill '{name}' created at {skill_file_path}."})

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")
