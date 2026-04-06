from dataclasses import dataclass

from byte import Event
from byte.tui.tui_component_events import TuiComponentEvent


class TuiEvents:
    """Namespace for all tui based event types."""

    @dataclass
    class UserInputSubmitted(Event):
        """Event emitted when user submits input."""

        message: str

    @dataclass
    class ComponentEvent(TuiComponentEvent):
        # TODO: This doc string is wrong
        """Event emitted when a Textual message needs to be displayed in the TUI."""

        event: TuiComponentEvent
