from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Awaitable, Callable, Dict, List, TypeVar, Union

from byte.event import Event

if TYPE_CHECKING:
    from byte.foundation import Application


T = TypeVar("T", bound=Event)
EventCallback = Union[Callable[[T], T | None], Callable[[T], Awaitable[T | None]]]


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
