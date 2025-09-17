from typing import Any, Optional

from byte.core.events.dispatcher import EventDispatcher
from byte.core.events.event import Event


class Eventable:
    """Mixin class that provides event dispatching capability to domain services.

    Enables services to emit events without direct coupling to the event system.
    Usage: `class FileService(Eventable): ...` then `await self.event(FileAdded(...))`
    """

    # Type hint for container attribute that will be provided by classes using this mixin
    container: Any
    _event_dispatcher: Optional[EventDispatcher]

    async def boot_eventable(self) -> None:
        """Boot method for Eventable mixin - automatically called by Command.__init__."""
        if hasattr(self, "container") and self.container:
            event_dispatcher = await self.container.make("event_dispatcher")
            self._event_dispatcher = event_dispatcher

    async def event(self, event: Event):
        """Dispatch an event through the configured dispatcher.

        Gracefully handles missing dispatcher to prevent service failures.
        Usage: `await self.event(FileAdded(file_path="/path/to/file"))`
        """
        if self._event_dispatcher:
            await self._event_dispatcher.dispatch(event)
