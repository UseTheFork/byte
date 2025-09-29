from typing import Annotated, TypedDict

from langgraph.graph.message import AnyMessage, add_messages

from byte.domain.agent.implementations.coder.edit_format.base import SearchReplaceBlock


class BaseState(TypedDict):
    """Base state that all agents inherit."""

    messages: Annotated[list[AnyMessage], add_messages]

    agent_status: str
    errors: list[AnyMessage]
    file_context: str


class CoderState(BaseState):
    """Coder-specific state with file context."""

    edit_format_system: str

    parsed_blocks: list[SearchReplaceBlock]
