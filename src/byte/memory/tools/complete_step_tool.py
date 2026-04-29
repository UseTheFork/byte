from datetime import UTC, datetime
from typing import override

from byte.orchestration import BaseState, PlanStep
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolRunException


class CompleteStepTool(BaseTool):
    name: str = "complete_step"
    description: str = (
        "Mark a step in the current plan as completed. Use the step's id to identify which step to complete."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "step_id": {
                "type": "string",
                "description": "The id of the plan step to mark as completed.",
            },
        },
        "required": ["step_id"],
    }

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")

    @override
    async def run(self, step_id: str, state: BaseState, **kwargs) -> ToolResult:
        plan: list[PlanStep] | None = state.get("plan")

        if not plan:
            raise ToolRunException("No active plan found in state.")

        updated_plan: list[PlanStep] = []
        found = False
        now = datetime.now(UTC).isoformat()

        for step in plan:
            if step["id"] == step_id:
                found = True
                updated_plan.append(
                    PlanStep(
                        id=step["id"],
                        order=step["order"],
                        content=step["content"],
                        note=step.get("note"),
                        status="completed",
                        created_at=step["created_at"],
                        updated_at=now,
                    )
                )
            else:
                updated_plan.append(step)

        if not found:
            raise ToolRunException(f"Step with id '{step_id}' not found in the current plan.")

        return ToolResult(
            result={
                "content": f"Step '{step_id}' marked as completed.",
            },
            extra={"plan": updated_plan},
        )
