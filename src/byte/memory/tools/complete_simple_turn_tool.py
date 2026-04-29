from datetime import UTC, datetime
from typing import override

from byte.support import Section
from byte.support.utils import list_to_multiline_text
from byte.tools import BaseTool, ToolResult


class CompleteSimpleTurnTool(BaseTool):
    name: str = "complete_turn_simple"
    description: str = "Mark the current agent turn as complete."
    input_schema = {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "A VERY short summary of the work done during this turn, visible to other agents in history.",
                "maxLength": 200,
            },
        },
        "required": ["summary"],
    }

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        summary = result.result.get("summary", "")

        completed_msg = [
            Section.sub_heading("Summary", 2),
            summary,
        ]

        return list_to_multiline_text(completed_msg)

    @override
    async def run(
        self,
        summary: str,
        **kwargs,
    ) -> ToolResult:

        now = datetime.now(UTC).isoformat()

        return ToolResult(
            result={
                "summary": summary,
                "completed_at": now,
            }
        )
