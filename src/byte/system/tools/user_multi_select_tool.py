from typing import Any, override

from byte.tools import BaseTool, ToolResult
from byte.tui import InteractionService
from byte.tui.schemas import Answer


class UserMultiSelectTool(BaseTool):
    name: str = "user_multi_select_tool"
    description: str = "Present the user with a list of choices and return their selections (multiple selections allowed)."
    input_schema = {
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

    @override
    async def run(
        self,
        question: str = "",
        choices: list[dict[str, Any]] | None = None,
        **kwargs,
    ) -> ToolResult:

        answer_options = [
            Answer(
                label=choice["label"],
                value=choice["value"],
                is_default=choice.get("is_default", False),
            )
            for choice in (choices or [])
        ]

        interaction_service = self.app.make(InteractionService)

        selected = await interaction_service.multi_select(question, answer_options)

        formatted_selections = [f"{answer.label} ({answer.value})" for answer in selected]
        selections_text = ", ".join(formatted_selections)

        return ToolResult(result={"content": f"User selected: {selections_text}"})

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")
