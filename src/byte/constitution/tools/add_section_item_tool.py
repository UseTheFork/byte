from typing import override

from byte.constitution.service.constitution_service import ConstitutionService
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolRunException


class AddSectionItemTool(BaseTool):
    name: str = "constitution_add_section_item_tool"
    description: str = "Add a named item to an existing constitution section."
    input_schema = {
        "type": "object",
        "properties": {
            "section_id": {
                "type": "string",
                "description": "ID of the parent section.",
            },
            "item_name": {
                "type": "string",
                "description": "Display name of the new item.",
            },
            "content": {
                "type": "string",
                "description": "Content of the item.",
            },
            "order": {
                "type": "integer",
                "description": "Display order of the item (e.g. 1, 2, 3). Defaults to 1.",
            },
        },
        "required": ["section_id", "item_name", "content"],
    }

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("message", "")

    @override
    async def run(self, section_id: str, item_name: str, content: str, order: int = 1, **kwargs) -> ToolResult:
        service = self.app.make(ConstitutionService)
        try:
            item = service.add_section_item(section_id=section_id, item_name=item_name, content=content, order=order)
        except (RuntimeError, ValueError) as exc:
            raise ToolRunException(str(exc)) from exc

        return ToolResult(result={"message": f"Added item '{item.name}' to section with id '{section_id}'."})
