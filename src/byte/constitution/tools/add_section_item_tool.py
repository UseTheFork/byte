from typing import override

from byte.constitution.service.constitution_service import ConstitutionService
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolRunException


class AddSectionItemTool(BaseTool):
    name: str = "constitution_add_section_item"
    description: str = "Add a named item to an existing constitution section."
    input_schema = {
        "type": "object",
        "properties": {
            "section_name": {
                "type": "string",
                "description": "Display name or slug of the parent section.",
            },
            "item_name": {
                "type": "string",
                "description": "Display name of the new item.",
            },
            "content": {
                "type": "string",
                "description": "Content of the item.",
            },
        },
        "required": ["section_name", "item_name", "content"],
    }

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("message", "")

    @override
    async def run(self, section_name: str, item_name: str, content: str, **kwargs) -> ToolResult:
        service = self.app.make(ConstitutionService)
        try:
            item = service.add_section_item(section_name=section_name, item_name=item_name, content=content)
        except (RuntimeError, ValueError) as exc:
            raise ToolRunException(str(exc)) from exc

        return ToolResult(result={"message": f"Added item '{item.name}' to section '{section_name}'."})
