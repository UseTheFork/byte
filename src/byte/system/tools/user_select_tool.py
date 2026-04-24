from typing import TYPE_CHECKING, Any, override

from langchain_core.tools import ArgsSchema

from byte.tools import BaseTool, ToolResult
from byte.tui import InteractionService
from byte.tui.schemas import Answer

if TYPE_CHECKING:
    from byte import Application

user_select_schema = {
    "type": "object",
    "properties": {
        "question": {
            "type": "string",
            "description": "The question to present to the user.",
        },
        "choices": {
            "type": "array",
            "description": "The list of choices to present to the user.",
            "items": {
                "type": "object",
                "properties": {
                    "label": {"type": "string", "description": "Display label for the choice."},
                    "value": {"description": "The value associated with the choice."},
                    "is_default": {"type": "boolean", "description": "Whether this choice is the default."},
                },
                "required": ["label", "value"],
            },
        },
    },
    "required": ["question", "choices"],
}


class UserSelectTool(BaseTool):
    name: str = "UserSelectTool"
    description: str = "Present the user with a list of choices and return their selection."
    args_schema: ArgsSchema | None = user_select_schema

    @override
    async def _arun(
        self,
        question: str = "",
        choices: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> ToolResult:
        app: Application = kwargs.get("app")  # ty:ignore[invalid-assignment]

        if app is None:
            raise RuntimeError("Application instance is required but was not provided")

        answer_options = [
            Answer(
                label=choice["label"],
                value=choice["value"],
                is_default=choice.get("is_default", False),
            )
            for choice in (choices or [])
        ]

        interaction_service = app.make(InteractionService)

        selected = await interaction_service.select(question, answer_options)

        return ToolResult(result=f"User selected: {selected.label} ({selected.value})")
