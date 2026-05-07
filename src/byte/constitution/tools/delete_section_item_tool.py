from typing import override

from byte.constitution.service.constitution_service import ConstitutionService
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolRunException


class DeleteSectionItemTool(BaseTool):
    name: str = "constitution_delete_section_item"
    description: str = "Remove a named item from an existing constitution section."
    input_schema = {
        "type": "object",
        "properties": {
            "section_name": {
                "type": "string",
                "description": "Display name or slug of the parent section.",
            },
            "item_name": {
                "type": "string",
                "description": "Display name or slug of the item to remove.",
            },
        },
        "required": ["section_name", "item_name"],
    }

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("message", "")

    @override
    async def run(self, section_name: str, item_name: str, **kwargs) -> ToolResult:
        service = self.app.make(ConstitutionService)
        try:
            service.delete_section_item(section_name=section_name, item_name=item_name)
        except (RuntimeError, ValueError) as exc:
            raise ToolRunException(str(exc)) from exc

        return ToolResult(result={"message": f"Deleted item '{item_name}' from section '{section_name}'."})
