from byte.orchestration.models.base_phase_model import BasePhaseModel


class RoutePhaseModel(BasePhaseModel):
    """A phase that auto-completes and routes to a target node, then returns to on_complete."""
