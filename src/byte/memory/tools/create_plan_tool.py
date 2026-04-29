from datetime import UTC, datetime
from typing import List, override

from byte.orchestration import PlanStep
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
                    "type": "object",
                    "properties": {
                        "order": {
                            "type": "integer",
                            "description": "The position of this step in the plan (1-based).",
                        },
                        "content": {
                            "type": "string",
                            "description": "The description of the task to be completed.",
                        },
                        "note": {
                            "type": "string",
                            "description": "An optional note or additional detail about the task.",
                        },
                    },
                    "required": ["order", "content"],
                },
            },
        },
        "required": ["steps"],
    }

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        plan = result.result.get("plan", [])
        steps = "\n".join(f"{step['order']}. {step['content']}" for step in plan)
        return f"Created plan with {len(plan)} steps:\n{steps}"

    @override
    async def run(self, steps: List[dict], **kwargs) -> ToolResult:

        now = datetime.now(UTC).isoformat()
        parsed_steps: List[PlanStep] = [
            PlanStep(
                id=str(step["order"]),
                order=step["order"],
                content=step["content"],
                note=step.get("note"),
                status="pending",
                created_at=now,
                updated_at=now,
            )
            for step in steps
        ]
        parsed_steps.sort(key=lambda s: s["order"])

        return ToolResult(
            result={
                "plan": parsed_steps,
            },
            extra={"plan": parsed_steps},
        )
