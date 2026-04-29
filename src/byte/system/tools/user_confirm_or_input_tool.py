from typing import override

from byte.tools import BaseTool, ToolResult
from byte.tui import InteractionService


class UserConfirmOrInputTool(BaseTool):
    name: str = "user_confirm_or_input"
    description: str = (
        "Ask the user a yes/no question. If they confirm, return True with no text. "
        "If they decline, prompt for text input and return the result."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "confirm_message": {
                "type": "string",
                "description": "The yes/no question to ask the user first.",
            },
            "input_message": {
                "type": "string",
                "description": "The text input prompt to show if the user declines.",
            },
            "default_confirm": {
                "type": "boolean",
                "description": "The default value for the confirmation prompt.",
            },
        },
        "required": ["confirm_message", "input_message"],
    }

    @override
    async def run(
        self,
        confirm_message: str = "",
        input_message: str = "",
        default_confirm: bool = True,
        **kwargs,
    ) -> ToolResult:

        interaction_service = self.app.make(InteractionService)

        confirmed, text_input = await interaction_service.confirm_or_input(
            confirm_message, input_message, default_confirm
        )

        if confirmed:
            return ToolResult(result={"content": "User confirmed yes."})

        return ToolResult(result={"content": f"User declined and provided input: {text_input}"})

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")
