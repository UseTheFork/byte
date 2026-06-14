from typing import Optional, override

from byte.skills import SkillLoaderService
from byte.support.yaml import Yaml
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolValidationException


class EditSkillTool(BaseTool):
    name: str = "edit_skill_tool"
    description: str = "Use this tool to edit an existing skill. Call this when you want to update a skill's description and/or instructions."
    input_schema = {
        "type": "object",
        "properties": {
            "skill_id": {
                "type": "string",
                "description": "The ID of the skill to edit.",
            },
            "description": {
                "type": "string",
                "description": "The new description of what the skill does. Optional.",
                "maxLength": 1024,
            },
            "instructions": {
                "type": "string",
                "description": "The new instructions body for the skill (written as markdown). Optional.",
            },
        },
        "required": ["skill_id"],
    }

    @override
    async def run(
        self,
        skill_id: str,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        **kwargs,
    ) -> ToolResult:
        # Validate that at least one optional field is provided
        if not any([description, instructions]):
            raise ToolValidationException("At least one of 'description' or 'instructions' must be provided.")

        skill_loader_service = self.app.make(SkillLoaderService)
        skill = skill_loader_service.get_skill(skill_id)
        if skill is None:
            raise ToolValidationException(f"Skill '{skill_id}' not found.")

        # Read existing SKILL.md file
        try:
            content = skill.skill_file_path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError) as exc:
            raise ToolValidationException(f"Could not read skill file {skill.skill_file_path}: {exc}")

        # Parse existing frontmatter
        try:
            frontmatter, body = Yaml.parse_frontmatter(content)
        except Exception as exc:
            raise ToolValidationException(f"Failed to parse frontmatter in {skill.skill_file_path}: {exc}")

        # Update frontmatter with provided values, keeping existing values for omitted fields
        new_description = description if description is not None else skill.description
        new_instructions = instructions if instructions is not None else body

        # Preserve version and other existing frontmatter fields
        updated_frontmatter = frontmatter.copy()
        updated_frontmatter["description"] = new_description

        # Render updated content
        updated_content = Yaml.render_frontmatter(updated_frontmatter, new_instructions)

        # Write updated content to SKILL.md in-place
        skill.skill_file_path.write_text(updated_content, encoding="utf-8")

        # Reload skill loader to pick up changes
        skill_loader_service.reload()

        final_name = skill.name

        return ToolResult(
            result={
                "skill_id": final_name,
                "content": f"Skill '{final_name}' updated.",
            },
        )

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")

    @classmethod
    def format_tui_message(cls, result: ToolResult) -> str:
        skill_id = result.result.get("skill_id", "")
        return f"Skill '{skill_id}' edited."
