from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from textual.message import Message

from byte import EventBus
from byte.event import Event

if TYPE_CHECKING:
    from byte.foundation import Application

T = TypeVar("T", bound=Event)


class Eventable:
    """Mixin that provides event emission capabilities through the event bus.

    Enables services to emit events with typed Pydantic payloads through the
    centralized event system. Events can be processed by registered listeners
    and transformed through the event pipeline for cross-domain communication.
    Usage: `class MyService(Eventable): result = await self.emit(payload)`
    """

    app: Application

    async def emit(self, payload: T) -> T:
        """Emit an event payload through the event bus system.

        Resolves the EventBus from the app and emits the payload,
        allowing registered listeners to process and potentially transform
        the event data before returning the final result.s
        """

        if not self.app:
            raise RuntimeError("No app available - ensure service is properly initialized")

        # TODO: Add if in debugging check here
        # self.app["log"].info(payload)

        event_bus = self.app.make(EventBus)
        return await event_bus.emit(
            payload,
        )

    async def emit_tui(self, payload: Message):
        """Emit a TUI event through the event bus system.

        Wraps the TuiEvents payload in Events.TuiEvent before emitting,
        allowing TUI-specific events to be processed by registered listeners.
        Usage: `await self.emit_tui(TuiEvents.ResponseStarted())`
        """

        if not self.app:
            raise RuntimeError("No app available - ensure service is properly initialized")

        byte_tui = self.app.tui()
        byte_tui.conversation.post_message(payload)
