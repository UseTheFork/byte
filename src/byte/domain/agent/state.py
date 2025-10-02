from typing import Annotated, TypedDict

from langgraph.graph.message import AnyMessage, add_messages

from byte.domain.edit_format.service.edit_format_service import SearchReplaceBlock


class BaseState(TypedDict):
    """Base state that all agents inherit."""

    messages: Annotated[list[AnyMessage], add_messages]

    agent: str

    agent_status: str
    errors: list[AnyMessage]


class CoderState(BaseState):
    """Coder-specific state with file context."""

    edit_format_system: str

    parsed_blocks: list[SearchReplaceBlock]


class AskState(CoderState):
    """"""

    pass
