from typing import Annotated, Literal, TypedDict

from langgraph.graph.message import AnyMessage, add_messages

from byte.orchestration import ConstraintSchema, MetadataSchema, add_constraints, replace_str, update_metadata


class PlanStep(TypedDict):
    """ """

    id: str
    content: str
    note: str | None
    status: Literal["pending", "in_progress", "completed"] | None
    order: int
    created_at: str
    updated_at: str


class RoutingState(TypedDict):
    """Routing information for graph node transitions.

    Usage: Tracks the current and target nodes during graph execution.
    """

    target: str
    source: str


class BaseState(TypedDict):
    """Base state that all agents inherit with messaging and status tracking.

    Usage: `state = BaseState(messages=[], agent="CoderAgent")`
    """

    # Persistent conversation history from memory store
    history_messages: Annotated[list[AnyMessage], add_messages]

    # Ephemeral messages for current execution only (validation, errors, etc.)
    scratch_messages: Annotated[list[AnyMessage], add_messages]

    final_message: AnyMessage | None

    # Current user request being processed by the agent
    user_request: str

    constraints: Annotated[list[ConstraintSchema], add_constraints]

    masked_messages: list[AnyMessage]

    errors: Annotated[str | None, replace_str]

    # These are specific to Coder
    touched_files: list[str]

    plan: list[PlanStep] | None

    routing: RoutingState

    is_cancelled: bool

    metadata: Annotated[MetadataSchema, update_metadata]
