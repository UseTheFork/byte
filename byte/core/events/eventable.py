from typing import Optional

from .dispatcher import EventDispatcher
from .event import Event


class Eventable:
    """Mixin class that provides event dispatching capability."""
    
    def __init__(self, event_dispatcher: Optional[EventDispatcher] = None):
        self._event_dispatcher = event_dispatcher
    
    async def event(self, event: Event):
        """Dispatch an event. Usage: await self.event(SomeEvent(...))"""
        if self._event_dispatcher:
            await self._event_dispatcher.dispatch(event)
