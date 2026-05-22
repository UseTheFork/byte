from typing import Annotated, Dict, TypedDict, Union

from langgraph.graph.message import AnyMessage, add_messages

from byte.orchestration import ConstraintSchema, MetadataSchema, PhaseModel, Reducer, RoutePhaseModel


class HarnessState(TypedDict):
    """State passed to a agents, constraining its skills, xyz."""

    spec: str
    skills: list[str]


class RoutingState(TypedDict):
    """Routing information for graph node transitions."""

    target: str
    source: str


class BaseState(TypedDict):
    """Base state that all agents inherit with messaging and status tracking."""

    harness: HarnessState

    # Persistent conversation history from memory store
    history_messages: Annotated[list[AnyMessage], add_messages]

    # Ephemeral messages for current execution only (validation, errors, etc.)
    scratch_messages: Annotated[list[AnyMessage], add_messages]

    final_message: AnyMessage | None

    # Current user request being processed by the agent
    user_request: str

    constraints: Annotated[list[ConstraintSchema], Reducer.add_constraints]

    errors: Annotated[str | None, Reducer.replace_str]

    # These are specific to Coder
    touched_files: list[str]

    workflow_phases: Dict[str, Union[PhaseModel | RoutePhaseModel]] | None

    routing: RoutingState

    is_cancelled: bool

    metadata: Annotated[MetadataSchema, Reducer.update_metadata]
