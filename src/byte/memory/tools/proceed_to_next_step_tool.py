from typing import override

from byte.tools import BaseTool, ToolResult
from byte.tui import InteractionService


class ProceedToNextStepTool(BaseTool):
    name: str = "proceed_to_next_step"
    description: str = (
        "Ask the user to confirm before proceeding to the next step. "
        "Use this tool whenever user approval is required before continuing."
    )
    input_schema = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")

    @override
    async def run(self, **kwargs) -> ToolResult:
        interaction_service = self.app.make(InteractionService)

        confirmed = await interaction_service.confirm("Proceed to the next step?", default=True)

        if confirmed:
            return ToolResult(result={"content": "User confirmed. Proceeding to the next step."})

        return ToolResult(result={"content": "User declined. Not proceeding to the next step."})
