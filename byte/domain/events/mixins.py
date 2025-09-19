from typing import Any, Optional

from byte.domain.events.dispatcher import EventDispatcher, EventResult
from byte.domain.events.event import Event


class Eventable:
    """Enhanced mixin with middleware-style event dispatching.

    Provides both fire-and-forget and result-returning event methods
    for different use cases throughout the application.
    Usage: `result = await self.dispatch_event(event)` -> EventResult with payload
    """

    container: Any
    _event_dispatcher: Optional[EventDispatcher]

    async def boot_eventable(self) -> None:
        """Boot method for Eventable mixin - automatically called by Command.__init__."""
        if hasattr(self, "container") and self.container:
            event_dispatcher = await self.container.make(EventDispatcher)
            self._event_dispatcher = event_dispatcher

    async def event(self, event: Event) -> None:
        """Fire-and-forget event dispatch for backward compatibility.

        Usage: `await self.event(FileAdded(file_path="/path/to/file"))`
        """
        if self._event_dispatcher:
            await self._event_dispatcher.dispatch(event)

    async def dispatch_event(self, event: Event) -> Optional[EventResult]:
        """Dispatch event and return result with modified payload.

        Enables middleware-style processing where services can react to
        the modified event payload and processing status.
        Usage: `result = await self.dispatch_event(FileValidation(file_path="main.py"))`
        """
        if self._event_dispatcher:
            return await self._event_dispatcher.dispatch(event)
        return None
