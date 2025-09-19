import asyncio
from typing import Callable, Dict, List, Optional, Type

from byte.core.service.mixins import Bootable
from byte.domain.events.event import Event


class EventResult:
    """Result container for event processing with middleware support."""

    def __init__(
        self, event: Event, success: bool = True, error: Optional[Exception] = None
    ):
        self.event = event
        self.success = success
        self.error = error
        self.stopped = event.stop_propagation
        self.prevented = event.prevent_default


class EventDispatcher(Bootable):
    """Enhanced event dispatcher with middleware-style processing.

    Supports event payload modification, propagation control, and result aggregation.
    Listeners can modify events and control further processing through return values.
    Usage: `result = await dispatcher.dispatch(event)` -> EventResult with modified payload
    """

    async def boot(self):
        # Group listeners by event type with priority support
        self._listeners: Dict[Type[Event], List[tuple[int, Callable]]] = {}
        self._middleware: List[Callable] = []

    def listen(self, event_type: Type[Event], listener: Callable, priority: int = 0):
        """Register an event listener with optional priority.

        Higher priority listeners execute first. Listeners can modify the event
        payload and control propagation through return values or event flags.
        Usage: `dispatcher.listen(PrePrompt, handle_pre_prompt, priority=100)`
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []

        self._listeners[event_type].append((priority, listener))
        # Sort by priority (higher first)
        self._listeners[event_type].sort(key=lambda x: x[0], reverse=True)

    def middleware(self, middleware_func: Callable):
        """Register global middleware that runs for all events.

        Middleware runs before specific listeners and can modify events
        or halt processing for all event types.
        Usage: `dispatcher.middleware(logging_middleware)`
        """
        self._middleware.append(middleware_func)

    async def dispatch(self, event: Event) -> EventResult:
        """Dispatch event through middleware and listeners with payload modification.

        Processes event through global middleware first, then specific listeners.
        Returns EventResult containing the modified event and processing status.
        Usage: `result = await dispatcher.dispatch(FileAdded(...))` -> modified event
        """
        try:
            # Run global middleware first
            for middleware in self._middleware:
                if event.stop_propagation:
                    break

                await self._execute_listener(middleware, event)

            # Run specific event listeners if not stopped
            if not event.stop_propagation:
                event_type = type(event)
                if event_type in self._listeners:
                    for priority, listener in self._listeners[event_type]:
                        if event.stop_propagation:
                            break
                        await self._execute_listener(listener, event)

            return EventResult(event, success=True)

        except Exception as e:
            return EventResult(event, success=False, error=e)

    async def _execute_listener(self, listener: Callable, event: Event):
        """Execute a single listener with proper async/sync handling.

        Supports listeners that return values to control event processing:
        - False: stop propagation
        - Dict: merge into event payload
        - None/True: continue processing
        """
        try:
            if asyncio.iscoroutinefunction(listener):
                result = await listener(event)
            else:
                result = listener(event)

            # Handle listener return values for middleware behavior
            if result is False:
                event.stop_propagation = True
            elif isinstance(result, dict):
                event.payload.update(result)

        except Exception as e:
            # Isolate listener failures but still log them
            print(f"Event listener error in {listener.__name__}: {e}")

    async def __call__(self, event: Event) -> EventResult:
        """Enable callable syntax for cleaner event dispatching.

        Usage: `result = await dispatcher(FileAdded(...))` -> EventResult
        """
        return await self.dispatch(event)
