from dataclasses import dataclass
from typing import TYPE_CHECKING

from byte import Event

if TYPE_CHECKING:
    pass


class TuiEvents:
    """Namespace for all tui based event types."""

    @dataclass
    class UserInputSubmitted(Event):
        """Event emitted when user submits input."""

        message: str
