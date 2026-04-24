from typing import TYPE_CHECKING, Any, Optional, override

from langchain_core.tools import ArgsSchema

from byte.tools import BaseTool, ToolResult
from byte.tui import InteractionService

if TYPE_CHECKING:
    from byte import Application

user_confirm_or_input_schema = {
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


class UserConfirmOrInputTool(BaseTool):
    name: str = "UserConfirmOrInputTool"
    description: str = (
        "Ask the user a yes/no question. If they confirm, return True with no text. "
        "If they decline, prompt for text input and return the result."
    )
    args_schema: ArgsSchema | None = user_confirm_or_input_schema

    @override
    async def _arun(
        self,
        confirm_message: str = "",
        input_message: str = "",
        default_confirm: bool = True,
        **kwargs: Any,
    ) -> ToolResult:
        app: Application = kwargs.get("app")  # ty:ignore[invalid-assignment]

        if app is None:
            raise RuntimeError("Application instance is required but was not provided")

        interaction_service = app.make(InteractionService)

        confirmed, text_input = await interaction_service.confirm_or_input(
            confirm_message, input_message, default_confirm
        )

        if confirmed:
            return ToolResult(result="User confirmed yes.")

        return ToolResult(result=f"User declined and provided input: {text_input}")
