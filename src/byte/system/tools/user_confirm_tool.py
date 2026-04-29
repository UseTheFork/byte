from typing import override

from byte.tools import BaseTool, ToolResult
from byte.tui import InteractionService


class UserConfirmTool(BaseTool):
    name: str = "user_confirm"
    description: str = "Ask the user a yes or no question and return their response."
    input_schema = {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The yes/no question to ask the user.",
            },
        },
        "required": ["question"],
    }

    @override
    async def run(
        self,
        question: str = "",
        **kwargs,
    ) -> ToolResult:

        interaction_service = self.app.make(InteractionService)

        confirmed = await interaction_service.confirm(question, True)

        if confirmed:
            return ToolResult(result={"content": "User confirmed yes."})

        return ToolResult(result={"content": "User declined with no."})

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")
