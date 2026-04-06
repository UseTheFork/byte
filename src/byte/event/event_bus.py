import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Awaitable, Callable, Dict, List, TypeVar, Union

from byte.event import Event

if TYPE_CHECKING:
    from byte.foundation import Application


T = TypeVar("T", bound=Event)
EventCallback = Union[Callable[[T], T | None], Callable[[T], Awaitable[T | None]]]


class EventPriority(Enum):
    """Event processing priority levels."""

    HIGH = 1  # UI updates, user interactions
    NORMAL = 2  # Business logic, file operations
    LOW = 3  # Background tasks, analytics


@dataclass
class QueuedEvent:
    """An event with metadata for queue processing."""

    event: Event
    priority: EventPriority
    sequence: int  # For stable sorting within same priority


class EventBus:
    """Production-grade async event bus with queue-based processing."""

    def __init__(self, app: Application):
        self.app = app
        self._listeners: Dict[type[Event], List[EventCallback]] = {}
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._processor_task: asyncio.Task | None = None
        self._running = False
        self._sequence_counter = 0
        self._processing_count = 0
        self._max_concurrent = 10  # Limit concurrent handler execution

    def on(self, event_type: type[T], callback: EventCallback[T]) -> None:
        """Register a listener for an event type.

        Usage: event_bus.on(FileAddedEvent, my_handler)
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    async def _handle_event_sync(self, event: T) -> T:
        """Execute all handlers for an event synchronously."""
        event_type = type(event)

        if event_type not in self._listeners:
            return event

        current_event = event

        for listener in self._listeners[event_type]:
            try:
                if asyncio.iscoroutinefunction(listener):
                    result = await listener(current_event)
                else:
                    result = listener(current_event)

                # Auto-chain: if listener returns an event, use it
                if result is not None:
                    current_event = result

            except Exception as e:
                self.app["log"].exception(e)
                print(f"Error in event listener for '{event_type.__name__}': {e}")

        return current_event

    async def _handle_event_async(self, event: T) -> None:
        """Handle a single event asynchronously."""
        try:
            result = await self._handle_event_sync(event)

            # Resolve completion future if waiting
            if hasattr(event, "_completion_future"):
                future = event._completion_future
                if not future.done():
                    future.set_result(result)

        except Exception as e:
            self.app["log"].exception(e)
            print(f"Error handling event {type(event).__name__}: {e}")

            # Reject completion future if waiting
            if hasattr(event, "_completion_future"):
                future = event._completion_future
                if not future.done():
                    future.set_exception(e)
        finally:
            self._processing_count -= 1

    async def _process_events(self) -> None:
        """Main event processing loop."""
        while self._running:
            try:
                # Wait for next event (blocks until available)
                _, _, queued = await self._queue.get()

                # Check for sentinel (shutdown signal)
                if queued is None:
                    break

                # Limit concurrent processing
                while self._processing_count >= self._max_concurrent:
                    await asyncio.sleep(0.01)

                # Process event in background task
                self._processing_count += 1
                asyncio.create_task(self._handle_event_async(queued.event))

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.app["log"].exception(e)
                print(f"Error in event processor: {e}")

    async def start(self) -> None:
        """Start the event processor. Call during application boot."""
        if self._processor_task is None or self._processor_task.done():
            self._running = True
            self._processor_task = asyncio.create_task(self._process_events())
            self.app["log"].info("EventBus processor started")

    async def stop(self) -> None:
        """Stop the event processor gracefully."""
        if self._processor_task:
            self._running = False
            # Send sentinel to wake up processor
            await self._queue.put((0, 0, None))
            try:
                await asyncio.wait_for(self._processor_task, timeout=5.0)
            except TimeoutError:
                self.app["log"].warning("EventBus processor did not stop gracefully")
                self._processor_task.cancel()
            self.app["log"].info("EventBus processor stopped")

    async def emit(self, event: T, priority: EventPriority = EventPriority.NORMAL, wait: bool = False) -> T:
        """Emit an event for async processing.

        Args:
            event: The event to emit
            priority: Processing priority (HIGH for UI events)
            wait: If True, wait for all handlers to complete before returning

        Usage:
            # Fire and forget (non-blocking)
            await event_bus.emit(TuiEvents.AskQuestion(...), priority=EventPriority.HIGH)

            # Wait for completion (blocking)
            result = await event_bus.emit(FileAddedEvent(...), wait=True)
        """
        if not self._running:
            # Fallback to synchronous processing if bus not started
            return await self._handle_event_sync(event)

        self._sequence_counter += 1
        queued = QueuedEvent(event=event, priority=priority, sequence=self._sequence_counter)

        # Priority queue uses (priority_value, sequence, item) for ordering
        await self._queue.put((priority.value, queued.sequence, queued))

        if wait:
            # Create a future to wait for completion
            future: asyncio.Future[T] = asyncio.Future()
            # Store future in event for processor to resolve
            event._completion_future = future  # type: ignore
            return await future

        return event
