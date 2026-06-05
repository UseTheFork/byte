from typing import override

from byte.orchestration import BaseState, HarnessStateUtils
from byte.tools import BaseTool, ToolResult


class BootstrapInstructionTool(BaseTool):
    name: str = "bootstrap_instruction_tool"
    description: str = "Load instruction into the agent harness based on the workflow requirements."
    input_schema = {
        "type": "object",
        "properties": {
            "instruction": {
                "type": "string",
                "description": "A short, clear, concise instruction to pass to the coding agent on exactly what must be done to complete the users task.",
            },
        },
        "required": ["instruction"],
    }

    @override
    async def run(
        self,
        state: BaseState,
        instruction: str,
        **kwargs,
    ) -> ToolResult:
        harness = HarnessStateUtils.get_harness(state)
        harness["instruction"] = instruction

        return ToolResult(
            result={"content": "OK", "instruction": instruction},
            extra={"harness": harness},
        )

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")

    @classmethod
    def format_tui_message(cls, result: ToolResult) -> str:
        """Format the tool result for display in the TUI."""
        return result.result.get("instruction", "")
