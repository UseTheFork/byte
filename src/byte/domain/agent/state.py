from typing import Annotated, TypedDict

from langgraph.graph.message import AnyMessage, add_messages

from byte.domain.agent.reducers import add_constraints, replace_str, update_metadata
from byte.domain.agent.schemas import ConstraintSchema, MetadataSchema
from byte.domain.prompt_format.schemas import SearchReplaceBlock


class BaseState(TypedDict):
    """Base state that all agents inherit with messaging and status tracking.

    Usage: `state = BaseState(messages=[], agent="CoderAgent")`
    """

    # Persistent conversation history from memory store
    history_messages: Annotated[list[AnyMessage], add_messages]

    # Ephemeral messages for current execution only (validation, errors, etc.)
    scratch_messages: Annotated[list[AnyMessage], add_messages]

    # Current user request being processed by the agent
    user_request: str

    constraints: Annotated[list[ConstraintSchema], add_constraints]
    masked_messages: list[AnyMessage]

    agent: str

    errors: Annotated[str | None, replace_str]
    examples: list[AnyMessage]

    extracted_content: str

    # These are specific to Coder
    edit_format_system: str
    parsed_blocks: list[SearchReplaceBlock]

    # This is specific to subprocess
    command: str

    metadata: Annotated[MetadataSchema, update_metadata]
