import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from byte import Event
from byte.tui.schemas import AnswerCancelled
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
    class PromptUser(TuiComponentEvent):
        """Request user input through an interactive prompt."""

        question: str
        result_future: asyncio.Future[Answer | list[Answer] | str | AnswerCancelled]
        prompt_type: Literal["select", "text", "multiselect"] = "text"
        options: list[Answer] | None = None
