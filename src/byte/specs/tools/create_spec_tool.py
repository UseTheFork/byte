import re
from typing import override

from byte.specs.service.spec_loader_service import SpecLoaderService
from byte.tools import BaseTool, ToolResult


class CreateSpecTool(BaseTool):
    name: str = "create_spec"
    description: str = (
        "Use this tool to create a new spec. Call this when you want to persist a spec with a topic, "
        "description, and instructions. The spec will be written as <topic>/SPEC.md with YAML frontmatter."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The topic slug for the spec (used as the subdirectory name). Lowercase, hyphens allowed.",
                "maxLength": 128,
            },
            "name": {
                "type": "string",
                "description": "The unique name of the spec stored in frontmatter.",
                "maxLength": 128,
            },
            "description": {
                "type": "string",
                "description": "A short description of what the spec covers.",
                "maxLength": 1024,
            },
            "instructions": {
                "type": "string",
                "description": "The body content of the spec (written as markdown after the frontmatter).",
            },
        },
        "required": ["topic", "name", "description", "instructions"],
    }

    @override
    async def run(
        self,
        topic: str = "",
        name: str = "",
        description: str = "",
        instructions: str = "",
        **kwargs,
    ) -> ToolResult:
        # Normalize topic: lowercase, replace invalid chars with hyphens, collapse/strip
        topic = topic.lower()
        topic = re.sub(r"[^a-z0-9]+", "-", topic)
        topic = re.sub(r"-+", "-", topic)
        topic = topic.strip("-")

        # Each spec lives in its own subdirectory: .byte/specs/<topic>/SPEC.md
        spec_file_path = self.app.specs_path(topic) / "SPEC.md"
        spec_file_path.parent.mkdir(parents=True, exist_ok=True)

        content = f"---\nname: {name}\ndescription: {description}\n---\n\n{instructions}\n"
        spec_file_path.write_text(content, encoding="utf-8")

        spec_loader_service = self.app.make(SpecLoaderService)
        spec_loader_service.reload()

        return ToolResult(result={"content": f"Spec '{name}' created at {spec_file_path}."})

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")
