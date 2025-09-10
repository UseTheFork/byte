import asyncio
from typing import Callable, Dict, List

from .event import Event


class EventDispatcher:
    """Event dispatcher for handling domain events."""
    
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
    
    def listen(self, event_type: str, listener: Callable):
        """Register an event listener."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)
    
    async def dispatch(self, event: Event):
        """Dispatch an event to all listeners."""
        event_type = event.__class__.__name__
        if event_type in self._listeners:
            for listener in self._listeners[event_type]:
                try:
                    if asyncio.iscoroutinefunction(listener):
                        await listener(event)
                    else:
                        listener(event)
                except Exception as e:
                    # Log error but don't stop other listeners
                    print(f"Event listener error: {e}")
    
    def __call__(self, event: Event):
        """Allow calling dispatcher as self.event(event)."""
        return self.dispatch(event)
