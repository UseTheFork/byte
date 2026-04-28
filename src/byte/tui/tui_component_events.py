from dataclasses import dataclass
from typing import TYPE_CHECKING

from textual.message import Message

if TYPE_CHECKING:
    from byte.tui.schemas import ChatMessage


# Sub events that specifically have to do with the TUI
class TuiComponentEvents:
    @dataclass
    class PromptSuggestion(Message):
        suggestion: str

    @dataclass
    class UserInputSubmitted(Message):
        body: str
        auto_complete: bool = False

    @dataclass
    class UserInputChanged(Message):
        value: str

    @dataclass
    class AgentResponseFailed(Message):
        """Sent when the agent fails to respond e.g. cant connect.
        Can be used to reset UI state."""

        last_message: ChatMessage

    @dataclass
    class NewUserMessage(Message):
        content: str
