from typing import override

from byte.constitution.service.constitution_service import ConstitutionService
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolRunException


class AddSectionTool(BaseTool):
    name: str = "constitution_add_section"
    description: str = (
        "Add a new section to the project constitution. "
        "Sections can optionally be scoped to specific file glob patterns."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Display name of the section (e.g. 'Security Requirements').",
            },
            "applies_to": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional glob patterns scoping this section to specific files (e.g. ['src/byte/node/**']). Omit for a global section.",
            },
        },
        "required": ["name"],
    }

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("message", "")

    @override
    async def run(self, name: str, applies_to: list[str] | None = None, **kwargs) -> ToolResult:
        service = self.app.make(ConstitutionService)
        try:
            section = service.add_section(name=name, applies_to=applies_to or None)
        except (RuntimeError, ValueError) as exc:
            raise ToolRunException(str(exc)) from exc

        return ToolResult(result={"message": f"Added section '{section.name}' to the constitution."})
