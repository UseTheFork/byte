from typing import TYPE_CHECKING, Optional, TypeVar

from byte.core.event_bus import EventBus, Payload

if TYPE_CHECKING:
    from byte.container import Container

T = TypeVar("T")


class Eventable:
    """Mixin that provides event emission capabilities through the event bus.

    Enables services to emit events with typed Pydantic payloads through the
    centralized event system. Events can be processed by registered listeners
    and transformed through the event pipeline for cross-domain communication.
    Usage: `class MyService(Eventable): result = await self.emit(payload)`
    """

    container: Optional["Container"]

    async def emit(self, payload: Payload) -> Payload:
        """Emit an event payload through the event bus system.

        Resolves the EventBus from the container and emits the payload,
        allowing registered listeners to process and potentially transform
        the event data before returning the final result.
        Usage: `result = await self.emit(Payload("user_action", {"key": "value"}))`
        """
        if not self.container:
            raise RuntimeError("No container available - ensure service is properly initialized")

        event_bus = await self.container.make(EventBus)
        return await event_bus.emit(payload)
