from datetime import UTC, datetime
from typing import override

from byte.orchestration import BaseState, PhaseModel
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolRunException
from byte.tui.service.interactions_service import InteractionService


class ConfirmCompletePlanStepTool(BaseTool):
    name: str = "confirm_complete_plan_step"
    description: str = (
        "Ask the user to confirm before proceeding to the next step."
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
                "description": "The status to set on the step. Defaults to 'completed'.",
                "default": "completed",
            },
        },
        "required": ["step_id", "status"],
    }

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")

    @override
    async def run(self, step_id: str, status: str, state: BaseState, **kwargs) -> ToolResult:
        plan: list[PhaseModel] | None = state.get("plan")

        if not plan:
            raise ToolRunException("No active plan found in state.")

        interaction_service = self.app.make(InteractionService)
        confirmed = await interaction_service.confirm("Proceed to the next step?", default=True)

        # TODO: Should this be an exception?
        if not confirmed:
            return ToolResult(result={"content": "User declined. Not proceeding to the next step."})

        updated_plan: list[PhaseModel] = []
        found = False
        now = datetime.now(UTC).isoformat()

        for step in plan:
            if step["id"] == step_id:
                found = True
                updated_plan.append(
                    PhaseModel(
                        **{
                            **step,
                            "status": status,
                            "updated_at": now,
                        }
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
