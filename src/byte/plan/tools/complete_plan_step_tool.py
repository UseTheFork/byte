from datetime import UTC, datetime
from typing import override

from byte.orchestration import BaseState
from byte.plan.models import PlanStep
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolRunException


class CompletePlanStepTool(BaseTool):
    name: str = "complete_plan_step"
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
            "status": {
                "type": "string",
                "enum": ["blocked", "completed"],
                "description": "The status to set on the step.",
            },
        },
        "required": ["step_id", "status"],
    }

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")

    @override
    async def run(self, step_id: str, status: str, state: BaseState, **kwargs) -> ToolResult:
        plan: list[PlanStep] | None = state.get("plan")

        if not plan:
            raise ToolRunException("No active plan found in state.")

        updated_plan: list[PlanStep] = []
        found = False
        now = datetime.now(UTC).isoformat()

        for step in plan:
            if step.id == step_id:
                found = True
                step_to_update = step
                step_to_update.status = status
                step_to_update.updated_at = now
                updated_plan.append(step_to_update)
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
