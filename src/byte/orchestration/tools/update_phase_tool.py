from typing import override

from byte.tools import BaseTool, ToolResult


class UpdatePhaseTool(BaseTool):
    name: str = "update_phase_tool"
    description: str = "Update the status of a phase. Only use this tool if explicitly stated in the phase instruction."
    input_schema = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        summary = result.result.get("content", "")
        return summary

    @override
    async def run(
        self,
        **kwargs,
    ) -> ToolResult:

        return ToolResult(
            result={
                "content": "OK",
            }
        )
