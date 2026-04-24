from typing import TYPE_CHECKING, Any, override

from langchain_core.tools import ArgsSchema

from byte.tools import BaseTool, ToolResult
from byte.tui import InteractionService

if TYPE_CHECKING:
    from byte import Application

user_input_text_schema = {
    "type": "object",
    "properties": {
        "question": {
            "type": "string",
            "description": "The prompt/question to ask the user for text input.",
        },
    },
    "required": ["question"],
}


class UserInputTextTool(BaseTool):
    name: str = "UserInputTextTool"
    description: str = "Ask the user for free-form text input and return their response."
    args_schema: ArgsSchema | None = user_input_text_schema

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

        text = await interaction_service.input_text(question)

        return ToolResult(result=text)
