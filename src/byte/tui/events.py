import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING

from byte import Event
from byte.tui.tui_component_events import TuiComponentEvent

if TYPE_CHECKING:
    from byte.tui.schemas import Answer


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

    @dataclass
    class AskQuestion(TuiComponentEvent):
        """Request user to answer a question."""

        question: str
        options: list[Answer]
        result_future: asyncio.Future[Answer]
