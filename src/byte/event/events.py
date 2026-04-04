from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from langchain_core.runnables import RunnableConfig

from byte.orchestration import BaseState

if TYPE_CHECKING:
    pass


@dataclass
class Event:
    """Base class for all events with optional metadata."""

    # timestamp: float = field(default_factory=lambda: time.time())
    # _metadata: dict[str, Any] = field(default_factory=dict)


class Events:
    """Namespace for all event types."""

    @dataclass
    class FileAdded(Event):
        """Event emitted when a file is added to context."""

        file_path: str
        mode: str
        action: str = "context_added"

    @dataclass
    class FileChanged(Event):
        # TODO: Doc String here.
        """"""

        file_path: str
        change_type: str

    @dataclass
    class UserInputSubmitted(Event):
        """Event emitted when user submits input."""

        message: str

    @dataclass
    class PostBoot(Event):
        """Event emitted after application boot to gather initialization info."""

        messages: list[str] = field(default_factory=list)

    @dataclass
    class PreAssistantNode(Event):
        """"""

        state: dict
        config: RunnableConfig

    @dataclass
    class EndNode(Event):
        """"""

        state: BaseState
        agent: str

    @dataclass
    class GatherReinforcement(Event):
        # TODO: Doc String here.
        """"""

        agent: str
        mode: str = "main"
        reinforcement: list[str] = field(default_factory=list)
        session_docs: list[str] = field(default_factory=list)
        system_context: list[str] = field(default_factory=list)

    @dataclass
    class GatherProjectContext(Event):
        # TODO: Doc String here.
        """"""

        conventions: list[str] = field(default_factory=list)
        session_docs: list[str] = field(default_factory=list)
        system_context: list[str] = field(default_factory=list)

    @dataclass
    class TuiEvent(Event):
        """Event emitted when a Textual message needs to be displayed in the TUI."""

        event: Event
