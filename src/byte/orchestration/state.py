from typing import Annotated, Dict, TypedDict, Union

from langgraph.graph.message import AnyMessage, add_messages

from byte.orchestration import (
    ConstraintSchema,
    MetadataSchema,
    PhaseModel,
    RoutePhaseModel,
    add_constraints,
    replace_str,
    update_metadata,
)


class HarnessState(TypedDict):
    """State passed to a harnessed agent, constraining its skills, tools, and prompt.

    Usage: Populated by the HarnessAgentNode before spawning an ExecutorAgentNode.
    """

    skills: list[str]
    tools: list[str]
    prompt: str | None


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

    harness: HarnessState | None

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

    workflow_phases: Dict[str, Union[PhaseModel | RoutePhaseModel]] | None

    routing: RoutingState

    is_cancelled: bool

    metadata: Annotated[MetadataSchema, update_metadata]
