from typing import override

from byte.constitution.service.constitution_service import ConstitutionService
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolRunException


class DeleteSectionTool(BaseTool):
    name: str = "constitution_delete_section_tool"
    description: str = "Remove a section from the project constitution by id."
    input_schema = {
        "type": "object",
        "properties": {
            "section_id": {
                "type": "string",
                "description": "ID of the section to remove.",
            },
        },
        "required": ["section_id"],
    }

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("message", "")

    @override
    async def run(self, section_id: str, **kwargs) -> ToolResult:
        service = self.app.make(ConstitutionService)
        try:
            service.delete_section(section_id=section_id)
        except (RuntimeError, ValueError) as exc:
            raise ToolRunException(str(exc)) from exc

        return ToolResult(result={"message": f"Deleted section with id '{section_id}' from the constitution."})
