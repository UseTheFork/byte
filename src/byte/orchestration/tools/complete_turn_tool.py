from datetime import UTC, datetime
from typing import override

from byte.orchestration import BaseState
from byte.support import Section
from byte.support.utils import list_to_multiline_text
from byte.tools import BaseTool, ToolResult


# AI:
class CompleteTurnTool(BaseTool):
    name: str = "complete_turn_tool"
    description: str = (
        "Mark the current agent turn as complete by providing a short summary of the work done during this turn. "
        "This summary will be shown to other agents when reviewing conversation history."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "A short summary of the work done during this turn, visible to other agents in history.",
            },
            "key_points": {
                "type": "array",
                "description": "An optional list of important outcomes or changes from this turn.",
                "items": {"type": "string"},
            },
        },
        "required": ["summary"],
    }
    terminates_turn = True

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        summary = result.result.get("summary", "")

        completed_msg = [
            Section.sub_heading("Summary", 2),
            summary,
        ]

        key_points = result.result.get("key_points", [])
        if key_points:
            completed_msg.append(Section.sub_heading("Key Points", 3))
            completed_msg.append("")

            for point in key_points:
                completed_msg.append(f"- {point}")

        return list_to_multiline_text(completed_msg)

    @override
    async def run(
        self,
        state: BaseState,
        summary: str,
        key_points: list[str] | None = None,
        **kwargs,
    ) -> ToolResult:

        now = datetime.now(UTC).isoformat()

        return ToolResult(
            result={
                "summary": summary,
                "key_points": key_points or [],
                "completed_at": now,
            }
        )
