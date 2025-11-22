import asyncio
import time
from enum import Enum
from typing import Any, Callable, Dict, List, TypeVar

from byte.core.array_store import ArrayStore
from byte.core.logging import log

T = TypeVar("T")


class EventType(Enum):
    POST_BOOT = "post_boot"

    PRE_PROMPT_TOOLKIT = "pre_prompt_toolkit"
    POST_PROMPT_TOOLKIT = "post_prompt_toolkit"

    GENERATE_FILE_CONTEXT = "generate_file_context"

    FILE_ADDED = "file_added"
    FILE_CHANGED = "file_changed"

    PRE_AGENT_EXECUTION = "pre_agent_execution"
    POST_AGENT_EXECUTION = "post_agent_execution"

    END_NODE = "end_node"

    PRE_ASSISTANT_NODE = "pre_assistant_node"
    POST_ASSISTANT_NODE = "post_assistant_node"

    GATHER_PROJECT_CONTEXT = "gather_project_context"
    GATHER_REINFORCEMENT = "gather_reinforcement"


class Payload:
    """Generic event payload that can carry any data using ArrayStore."""

    def __init__(
        self,
        event_type: EventType,
        data: ArrayStore | dict[str, Any] | None = None,
        timestamp: float | None = None,
    ):
        """Initialize a Payload with event type and optional data.

        Usage: `payload = Payload(EventType.FILE_ADDED, {"path": "file.py"})`
        """
        self.event_type = event_type
        self.timestamp = timestamp if timestamp is not None else time.time()

        # Ensure data is an ArrayStore instance
        if data is None:
            self.data = ArrayStore()
        elif isinstance(data, ArrayStore):
            self.data = data
        elif isinstance(data, dict):
            self.data = ArrayStore(data)
        else:
            self.data = ArrayStore()

    def get(self, key: str, default: Any = None) -> Any:
        """Get data value with optional default."""
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> "Payload":
        """Update the data store with a key-value pair and return self."""
        self.data.add(key, value)
        return self

    def update(self, updates: Dict[str, Any]) -> "Payload":
        """Merge multiple updates into the data store and return self."""
        self.data.merge(updates)
        return self


class EventBus:
    """Simple event system with typed Pydantic payloads."""

    def __init__(self, container=None, **kwargs):
        self.container = container
        self._listeners: Dict[str, List[Callable]] = {}

    def on(self, event_name: str, callback: Callable):
        """Register a listener for an event."""
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)

    async def emit(self, payload: Payload) -> Payload:
        """Emit an event using the payload's event_type."""
        event_name = payload.event_type.value

        if event_name not in self._listeners:
            return payload

        current_payload = payload

        for listener in self._listeners[event_name]:
            try:
                if asyncio.iscoroutinefunction(listener):
                    result = await listener(current_payload)
                else:
                    result = listener(current_payload)

                if result is not None:
                    current_payload = result

            except Exception as e:
                log.exception(e)
                print(f"Error in event listener for '{event_name}': {e}")

        return current_payload
