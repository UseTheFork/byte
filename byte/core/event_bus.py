import asyncio
import time
from enum import Enum
from typing import Any, Callable, Dict, List, TypeVar

from pydantic.dataclasses import dataclass as pydantic_dataclass

T = TypeVar("T")


class EventType(Enum):
    PRE_PROMPT_TOOLKIT = "pre_prompt_toolkit"

    FILE_ADDED = "file_added"


@pydantic_dataclass
class Payload:
    """Generic event payload that can carry any data."""

    event_type: EventType
    data: Dict[str, Any]
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()

    def get(self, key: str, default: Any = None) -> Any:
        """Get data value with optional default."""
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> "Payload":
        """Return new Payload with updated data."""
        new_data = self.data.copy()
        new_data[key] = value
        return Payload(
            event_type=self.event_type, data=new_data, timestamp=self.timestamp
        )

    def update(self, updates: Dict[str, Any]) -> "Payload":
        """Return new Payload with multiple updates."""
        new_data = self.data.copy()
        new_data.update(updates)
        return Payload(
            event_type=self.event_type, data=new_data, timestamp=self.timestamp
        )


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
                print(f"Error in event listener for '{event_name}': {e}")

        return current_payload
