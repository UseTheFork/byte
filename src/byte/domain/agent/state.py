from typing import Annotated, TypedDict

from langgraph.graph.message import AnyMessage, add_messages

from byte.domain.agent.reducers import add_constraints, replace_str
from byte.domain.agent.schemas import ConstraintSchema
from byte.domain.prompt_format.service.edit_format_service import SearchReplaceBlock


class BaseState(TypedDict):
    """Base state that all agents inherit with messaging and status tracking.

    Usage: `state = BaseState(messages=[], agent="CoderAgent")`
    """

    messages: Annotated[list[AnyMessage], add_messages]
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
