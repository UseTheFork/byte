from typing import TYPE_CHECKING, Any, Dict, List, Union

from byte.orchestration import UserConfirmPhaseTool

if TYPE_CHECKING:
    from byte.orchestration import BaseState, PhaseModel, RoutePhaseModel


class PhaseUtils:
    """Manage workflow phase utilities."""

    @staticmethod
    def inject_phase_input_schema_args(tool_schema: Dict[str, Any] | None) -> Dict[str, Any]:
        """Inject phase_id and phase_status arguments into tool input schema."""

        if not tool_schema:
            return {}

        if "properties" not in tool_schema["input_schema"]:
            tool_schema["input_schema"]["properties"] = {}
        existing_properties = tool_schema["input_schema"]["properties"]
        required = tool_schema["input_schema"].setdefault("required", [])

        new_properties: Dict[str, Any] = {}

        if "phase_id" not in existing_properties:
            new_properties["phase_id"] = {
                "type": "string",
                "description": "The id of the phase that this tool call is for. (Example: `phase-1`, `phase-2`)",
            }

        if "phase_status" not in existing_properties:
            new_properties["phase_status"] = {
                "type": "string",
                "enum": ["pending", "in_progress", "blocked", "completed"],
                "description": "The status to set on the phase. If a phase requires multiple tool calls or edits use `in_progress`. `completed` should only be used on the final tool call for the phase you are working on.",
            }

        new_properties.update(existing_properties)
        tool_schema["input_schema"]["properties"] = new_properties

        for field in ("phase_id", "phase_status"):
            if field not in required:
                required.insert(0, field)

        return tool_schema

    @staticmethod
    def to_phase_dict(phases: List[PhaseModel]) -> Dict[str, PhaseModel]:
        """Convert phases list to dictionary keyed by phase ID."""
        phase_dict: Dict[str, PhaseModel] = {}

        for phase in phases:
            phase_dict[f"phase-{phase.id}"] = phase

        return phase_dict

    @staticmethod
    def get_pending_phase(state: BaseState) -> Union[RoutePhaseModel | PhaseModel] | None:
        """Retrieve the first pending or in-progress phase from workflow."""
        workflow_phases = state.get("workflow_phases") or {}
        pending_phase = next(
            (phase for phase in workflow_phases.values() if phase.status in ("pending", "in_progress")), None
        )

        return pending_phase

    @staticmethod
    def get_workflow_phases(state: BaseState) -> Dict[str, Union[RoutePhaseModel | PhaseModel]] | None:
        """Get all workflow phases from state, or None if empty."""
        workflow_phases = state.get("workflow_phases") or {}
        if len(workflow_phases.keys()) <= 0:
            return None

        return workflow_phases

    @staticmethod
    def is_workflow_complete(state: BaseState) -> bool:
        """Check if all workflow phases are completed or blocked."""
        workflow_phases = state.get("workflow_phases") or {}

        # If this is not a workflow agent then we return true regardless
        if not PhaseUtils.is_workflow_agent(state):
            return True

        # TODO: add a enum for the status
        if workflow_phases and all(phase.status in ("completed", "blocked") for phase in workflow_phases.values()):
            return True

        return False

    @staticmethod
    def is_workflow_agent(state: BaseState) -> bool:
        """Check if state contains workflow phases."""
        workflow_phases = state.get("workflow_phases") or {}
        return len(workflow_phases.keys()) > 0

    @staticmethod
    def update_phase_with_tool_args(
        tool_call: Dict[str, Any], workflow_phases: Dict[str, Union[RoutePhaseModel | PhaseModel]] = {}
    ) -> Dict[str, Union[RoutePhaseModel | PhaseModel]]:
        """Update phase status based on tool call arguments."""
        tool_name = tool_call.get("name", None)
        if tool_name == UserConfirmPhaseTool.name:
            return workflow_phases

        args = tool_call.get("args", {})
        phase_id = args.get("phase_id", None)
        phase_status = args.get("phase_status", "pending")

        if phase_id:
            workflow_phases[phase_id].status = phase_status

        return workflow_phases

    # @staticmethod
    # def get_phase_redirect(args: Dict, workflow_phases: Dict[str, Union[RoutePhaseModel | PhaseModel]]) -> str | None:
    #     """Return the on_complete route target if the phase just completed."""
    #     phase_id = args.get("phase_id")
    #     phase_status = args.get("phase_status")

    #     if phase_id and phase_status == "completed":
    #         phase = workflow_phases.get(phase_id)
    #         if phase and phase.on_complete is not None:
    #             return Str.class_to_snake_case(phase.on_complete)

    #     return None
