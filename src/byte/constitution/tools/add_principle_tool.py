from typing import override

from byte.constitution.service.constitution_service import ConstitutionService
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolRunException


class AddPrincipleTool(BaseTool):
    name: str = "constitution_add_principle"
    description: str = (
        "Add a new core principle to the project constitution. "
        "Each principle has a display name (e.g. 'I. Library-First') and a description."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Display name of the principle (e.g. 'I. Library-First').",
            },
            "description": {
                "type": "string",
                "description": "Full text describing the principle.",
            },
        },
        "required": ["name", "description"],
    }

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("message", "")

    @override
    async def run(self, name: str, description: str, **kwargs) -> ToolResult:
        service = self.app.make(ConstitutionService)
        try:
            principle = service.add_principle(name=name, description=description)
        except (RuntimeError, ValueError) as exc:
            raise ToolRunException(str(exc)) from exc

        return ToolResult(
            result={"message": f"Added principle '{principle.name}' to the constitution."}
        )
