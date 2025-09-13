from dataclasses import dataclass

from byte.core.events.event import Event


@dataclass
class ExitRequested(Event):
    """Event emitted when the application should exit gracefully.

    Usage: `await self.event(ExitRequested())` -> triggers application shutdown
    """

    pass
