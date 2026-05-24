from typing import override

from byte.constitution.service.constitution_service import ConstitutionService
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolRunException


class DeleteGovernanceRuleTool(BaseTool):
    name: str = "constitution_delete_governance_rule_tool"
    description: str = "Remove a governance rule from the project constitution by id."
    input_schema = {
        "type": "object",
        "properties": {
            "rule_id": {
                "type": "string",
                "description": "ID of the governance rule to remove.",
            },
        },
        "required": ["rule_id"],
    }

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("message", "")

    @override
    async def run(self, rule_id: str, **kwargs) -> ToolResult:
        service = self.app.make(ConstitutionService)
        try:
            service.delete_governance_rule(rule_id=rule_id)
        except (RuntimeError, ValueError) as exc:
            raise ToolRunException(str(exc)) from exc

        return ToolResult(result={"message": f"Deleted governance rule with id '{rule_id}' from the constitution."})
