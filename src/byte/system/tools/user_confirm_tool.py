from typing import TYPE_CHECKING, Any, override

from langchain_core.tools import ArgsSchema

from byte.tools import BaseTool, ToolResult
from byte.tui import InteractionService

if TYPE_CHECKING:
    from byte import Application

user_confirm_schema = {
    "type": "object",
    "properties": {
        "question": {
            "type": "string",
            "description": "The yes/no question to ask the user.",
        },
    },
    "required": ["question"],
}


class UserConfirmTool(BaseTool):
    name: str = "UserConfirmTool"
    description: str = "Ask the user a yes or no question and return their response."
    args_schema: ArgsSchema | None = user_confirm_schema

    @override
    async def _arun(
        self,
        question: str = "",
        **kwargs: Any,
    ) -> ToolResult:
        app: Application = kwargs.get("app")  # ty:ignore[invalid-assignment]

        if app is None:
            raise RuntimeError("Application instance is required but was not provided")

        interaction_service = app.make(InteractionService)

        confirmed = await interaction_service.confirm(question, True)

        if confirmed:
            return ToolResult(result="User confirmed yes.")

        return ToolResult(result="User declined with no.")
