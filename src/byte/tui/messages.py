from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from textual.content import Content
from textual.message import Message
from textual.widget import Widget

if TYPE_CHECKING:
    from byte.tui.schemas import ChatMessage
    from byte.tui.widgets.chatbox import Chatbox


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

    @dataclass
    class UserInputChanged(Message):
        value: str

    @dataclass
    class AgentResponseStarted(Message):
        pass

    @dataclass
    class AgentResponseComplete(Message):
        chat_id: int | None
        message: ChatMessage
        chatbox: Chatbox

    @dataclass
    class AgentResponseFailed(Message):
        """Sent when the agent fails to respond e.g. cant connect.
        Can be used to reset UI state."""

        last_message: ChatMessage

    @dataclass
    class NewUserMessage(Message):
        content: str

    @dataclass
    class HistoryMove(Message):
        """Getting a new item form history."""

        direction: Literal[-1, +1]
        body: str

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
