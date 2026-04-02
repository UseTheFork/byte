from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Awaitable, Callable, Dict, List, TypeVar, Union

from langchain_core.runnables import RunnableConfig

from byte.orchestration import BaseState

if TYPE_CHECKING:
    from byte.foundation import Application


# class EventType(str, Enum):
#     POST_BOOT = "post_boot"

#     USER_INPUT_SUBMITTED = "user_input_submitted"

#     PRE_PROMPT_TOOLKIT = "pre_prompt_toolkit"
#     POST_PROMPT_TOOLKIT = "post_prompt_toolkit"

#     GENERATE_FILE_CONTEXT = "generate_file_context"

#     FILE_ADDED = "file_added"
#     FILE_CHANGED = "file_changed"

#     PRE_AGENT_EXECUTION = "pre_agent_execution"
#     POST_AGENT_EXECUTION = "post_agent_execution"

#     END_NODE = "end_node"

#     PRE_ASSISTANT_NODE = "pre_assistant_node"
#     POST_ASSISTANT_NODE = "post_assistant_node"

#     GATHER_AVAILABLE_CONVENTIONS = "gather_available_conventions"

#     GATHER_PROJECT_CONTEXT = "gather_project_context"
#     GATHER_REINFORCEMENT = "gather_reinforcement"

#     TEST = "test"


@dataclass
class Event:
    """Base class for all events with optional metadata."""

    # timestamp: float = field(default_factory=lambda: time.time())
    # _metadata: dict[str, Any] = field(default_factory=dict)


T = TypeVar("T", bound=Event)

# Add near the top with other type definitions
EventCallback = Union[Callable[[T], T | None], Callable[[T], Awaitable[T | None]]]


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

        messages: str

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

    # @dataclass
    # class GatherReinforcement(Event):
    #     # TODO: Doc String here.
    #     """"""

    #     user_input: str | None = None
    #     interrupted: bool = False
    #     active_agent: BaseAgent | None = None

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


class EventBus:
    """Simple event system with typed dataclass events."""

    def __init__(self, app: Application):
        self.app = app
        self._listeners: Dict[type[Event], List[Callable]] = {}

    def on(self, event_type: type[T], callback: EventCallback[T]) -> None:
        """Register a listener for an event type.

        Usage: event_bus.on(FileAddedEvent, my_handler)
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    async def emit(self, event: T) -> T:
        """Emit an event and return the potentially modified event.

        Usage: result = await event_bus.emit(FileAddedEvent(file_path="test.py", mode="editable"))
        """
        event_type = type(event)

        if event_type not in self._listeners:
            return event

        current_event = event

        for listener in self._listeners[event_type]:
            try:
                if asyncio.iscoroutinefunction(listener):
                    result = await listener(current_event)
                else:
                    result = listener(current_event)

                # Auto-chain: if listener returns an event, use it; otherwise keep current
                if result is not None:
                    current_event = result

            except Exception as e:
                self.app["log"].exception(e)
                print(f"Error in event listener for '{event_type.__name__}': {e}")

        return current_event
