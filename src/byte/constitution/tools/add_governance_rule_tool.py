from typing import override

from byte.constitution.service.constitution_service import ConstitutionService
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolRunException


class AddGovernanceRuleTool(BaseTool):
    name: str = "constitution_add_governance_rule_tool"
    description: str = "Add a named governance rule to the project constitution."
    input_schema = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Display name of the governance rule (e.g. 'Supremacy').",
            },
            "content": {
                "type": "string",
                "description": "Content of the governance rule.",
            },
            "order": {
                "type": "integer",
                "description": "Display order of the governance rule (e.g. 1, 2, 3). Defaults to 1.",
            },
        },
        "required": ["name", "content"],
    }

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("message", "")

    @override
    async def run(self, name: str, content: str, order: int = 1, **kwargs) -> ToolResult:
        service = self.app.make(ConstitutionService)
        try:
            rule = service.add_governance_rule(name=name, content=content, order=order)
        except (RuntimeError, ValueError) as exc:
            raise ToolRunException(str(exc)) from exc

        return ToolResult(result={"message": f"Added governance rule '{rule.name}' to the constitution."})
