import asyncio
from typing import Callable, Dict, List

from byte.domain.events.event import Event


class EventDispatcher:
    """Event dispatcher implementing the Observer pattern for domain events.

    Decouples event producers from consumers, enabling loose coupling between domains.
    Usage: `dispatcher.listen("FileAdded", handle_file_added)` then `await dispatcher.dispatch(FileAdded(...))`
    """

    def __init__(self):
        # Group listeners by event type for efficient lookup
        self._listeners: Dict[str, List[Callable]] = {}

    def listen(self, event_type: str, listener: Callable):
        """Register an event listener for a specific event type.

        Usage: `dispatcher.listen("FileAdded", lambda event: print(event.file_path))`
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)

    async def dispatch(self, event: Event):
        """Dispatch an event to all registered listeners.

        Handles both sync and async listeners, continuing execution even if individual listeners fail.
        Usage: `await dispatcher.dispatch(FileAdded(file_path="/path/to/file"))`
        """
        event_type = event.__class__.__name__
        if event_type in self._listeners:
            for listener in self._listeners[event_type]:
                try:
                    # Support both async and sync listeners for flexibility
                    if asyncio.iscoroutinefunction(listener):
                        await listener(event)
                    else:
                        listener(event)
                except Exception as e:
                    # Isolate listener failures to prevent cascade failures
                    print(f"Event listener error: {e}")

    def __call__(self, event: Event):
        """Enable callable syntax for cleaner event dispatching.

        Usage: `await dispatcher(FileAdded(...))` instead of `await dispatcher.dispatch(...)`
        """
        return self.dispatch(event)
