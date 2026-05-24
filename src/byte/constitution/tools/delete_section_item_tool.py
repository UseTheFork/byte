from typing import override

from byte.constitution.service.constitution_service import ConstitutionService
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolRunException


class DeleteSectionItemTool(BaseTool):
    name: str = "constitution_delete_section_item_tool"
    description: str = "Remove a named item from an existing constitution section."
    input_schema = {
        "type": "object",
        "properties": {
            "section_id": {
                "type": "string",
                "description": "ID of the parent section.",
            },
            "item_id": {
                "type": "string",
                "description": "ID of the item to remove.",
            },
        },
        "required": ["section_id", "item_id"],
    }

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("message", "")

    @override
    async def run(self, section_id: str, item_id: str, **kwargs) -> ToolResult:
        service = self.app.make(ConstitutionService)
        try:
            service.delete_section_item(section_id=section_id, item_id=item_id)
        except (RuntimeError, ValueError) as exc:
            raise ToolRunException(str(exc)) from exc

        return ToolResult(result={"message": f"Deleted item with id '{item_id}' from section with id '{section_id}'."})
