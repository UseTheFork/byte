from typing import override

from byte.constitution.service.constitution_service import ConstitutionService
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolRunException


class DeletePrincipleTool(BaseTool):
    name: str = "constitution_delete_principle_tool"
    description: str = "Remove a core principle from the project constitution by id."
    input_schema = {
        "type": "object",
        "properties": {
            "principle_id": {
                "type": "string",
                "description": "ID of the principle to remove.",
            },
        },
        "required": ["principle_id"],
    }

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("message", "")

    @override
    async def run(self, principle_id: str, **kwargs) -> ToolResult:
        service = self.app.make(ConstitutionService)
        try:
            service.delete_principle(principle_id=principle_id)
        except (RuntimeError, ValueError) as exc:
            raise ToolRunException(str(exc)) from exc

        return ToolResult(result={"message": f"Deleted principle with id '{principle_id}' from the constitution."})
