from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from byte.foundation.event_bus import EventBus, Payload

if TYPE_CHECKING:
    from byte.foundation import Application

T = TypeVar("T")


class Eventable:
    """Mixin that provides event emission capabilities through the event bus.

    Enables services to emit events with typed Pydantic payloads through the
    centralized event system. Events can be processed by registered listeners
    and transformed through the event pipeline for cross-domain communication.
    Usage: `class MyService(Eventable): result = await self.emit(payload)`
    """

    app: Application

    async def emit(self, payload: Payload) -> Payload:
        """Emit an event payload through the event bus system.

        Resolves the EventBus from the app and emits the payload,
        allowing registered listeners to process and potentially transform
        the event data before returning the final result.
        Usage: `result = await self.emit(Payload("user_action", {"key": "value"}))`
        """
        if not self.app:
            raise RuntimeError("No app available - ensure service is properly initialized")

        event_bus = await self.app.make(EventBus)
        return await event_bus.emit(payload)
