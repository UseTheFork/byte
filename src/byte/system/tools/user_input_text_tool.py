from typing import override

from byte.tools import BaseTool, ToolResult
from byte.tui import InteractionService


class UserInputTextTool(BaseTool):
    name: str = "user_input_text"
    description: str = "Ask the user for free-form text input and return their response."
    input_schema = {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The prompt/question to ask the user for text input.",
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

        text = await interaction_service.input_text(question)

        return ToolResult(result={"content": text})

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")
