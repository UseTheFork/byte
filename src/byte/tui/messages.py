from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from textual.content import Content
from textual.message import Message
from textual.widget import Widget

if TYPE_CHECKING:
    pass


class Messages:
    @dataclass
    class PromptSuggestion(Message):
        suggestion: str

    @dataclass
    class Dismiss(Message):
        widget: Widget

        @property
        def control(self) -> Widget:
            return self.widget

    @dataclass
    class UserInputSubmitted(Message):
        body: str
        auto_complete: bool = False

    # TODO: Do we need this?
    @dataclass
    class UserInputChanged(Message):
        value: str

    @dataclass
    class Flash(Message):
        """Request a message flash.

        Args:
            Message: Content of flash.
            style: Semantic style.
            duration: Duration in seconds or `None` for default.
        """

        content: str | Content
        style: Literal["default", "warning", "success", "error"]
        duration: float | None = None
