from typing import TYPE_CHECKING

from langchain_core.messages import ToolMessage

if TYPE_CHECKING:
    from byte.orchestration import BaseState


class State:
    """State helper utilities."""

    @staticmethod
    def has_plan(state: BaseState) -> bool:
        """ """
        return bool(state.get("plan"))

    @staticmethod
    def tool_was_called(state: BaseState, tool_name: str) -> bool:
        """Return True if a ToolMessage with the given tool name exists in scratch_messages."""
        return any(isinstance(m, ToolMessage) and m.name == tool_name for m in state.get("scratch_messages", []))
