from typing import Optional

from byte.core.events.dispatcher import EventDispatcher
from byte.core.events.event import Event


class Eventable:
    """Mixin class that provides event dispatching capability to domain services.
    
    Enables services to emit events without direct coupling to the event system.
    Usage: `class FileService(Eventable): ...` then `await self.event(FileAdded(...))`
    """

    def __init__(self, event_dispatcher: Optional[EventDispatcher] = None):
        # Optional dispatcher allows services to work without events if needed
        self._event_dispatcher = event_dispatcher

    async def event(self, event: Event):
        """Dispatch an event through the configured dispatcher.
        
        Gracefully handles missing dispatcher to prevent service failures.
        Usage: `await self.event(FileAdded(file_path="/path/to/file"))`
        """
        if self._event_dispatcher:
            await self._event_dispatcher.dispatch(event)
