from typing import override

from byte.tools import BaseTool, ToolResult
from byte.tui import InteractionService


class UserConfirmPhaseTool(BaseTool):
    name: str = "user_confirm_phase_complete_tool"
    description: str = (
        "Presents the current phase output to the user and asks them to confirm it as complete or provide feedback. "
        "If the user confirms, the phase status is marked as 'complete' and the workflow advances. "
        "If the user declines, their feedback is returned so the agent can revise and retry."
    )
    input_schema = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    @override
    async def run(
        self,
        phase_id,
        state,
        **kwargs,
    ) -> ToolResult:

        interaction_service = self.app.make(InteractionService)

        confirmed, text_input = await interaction_service.confirm_or_input(f"Complete {phase_id}", "Response", True)

        # TODO: convert status to a enum.
        if confirmed:
            workflow_phases = state["workflow_phases"]
            workflow_phases[phase_id].status = "complete"

            return ToolResult(
                result={"content": f"User confirmed {phase_id} as complete."},
                extra={"workflow_phases": workflow_phases},
            )

        return ToolResult(result={"content": f"User declined {phase_id} completion and provided input: {text_input}"})

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")
