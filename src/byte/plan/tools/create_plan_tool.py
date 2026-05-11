from typing import List, override

from byte.tools import BaseTool, ToolResult


class CreatePlanTool(BaseTool):
    name: str = "create_plan"
    description: str = (
        "Create a structured plan composed of ordered steps for completing the current request."
        "Use this to break down complex tasks into a clear, sequential list before executing them."
    )

    input_schema = {
        "type": "object",
        "properties": {
            "steps": {
                "type": "array",
                "description": "An ordered list of steps that make up the plan.",
                "items": {
                    "type": "string",
                    "description": "A single step description.",
                },
            },
        },
        "required": ["steps"],
        "additionalProperties": False,
    }

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        plan = result.result.get("plan", [])
        steps_text = "\n".join(f"{i}. {step}" for i, step in enumerate(plan, start=1))
        return f"Created plan with {len(plan)} steps:\n{steps_text}"

    @override
    async def run(self, steps: List[str], **kwargs) -> ToolResult:
        # Pass strings through directly as the plan
        return ToolResult(result={"plan": steps})
