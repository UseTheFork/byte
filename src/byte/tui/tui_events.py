from dataclasses import dataclass
from typing import TYPE_CHECKING

from byte.event import Event

if TYPE_CHECKING:
    from byte.tui.schemas import ChatMessage


# Sub events that specifically have to do with the TUI
class TuiEvents:
    @dataclass
    class CommandExecutionStarted(Event):
        pass

    @dataclass
    class CommandExecutionCompleted(Event):
        pass

    @dataclass
    class AddHeading(Event):
        heading: str

    @dataclass
    class ResponseStarted(Event):
        pass

    @dataclass
    class ResponseChunk(Event):
        chunk: str

    @dataclass
    class ResponseComplete(Event):
        pass

    @dataclass
    class PromptSuggestion(Event):
        suggestion: str

    @dataclass
    class UserInputSubmitted(Event):
        body: str
        auto_complete: bool = False

    @dataclass
    class UserInputChanged(Event):
        value: str

    @dataclass
    class AgentResponseFailed(Event):
        """Sent when the agent fails to respond e.g. cant connect.
        Can be used to reset UI state."""

        last_message: ChatMessage

    @dataclass
    class NewUserMessage(Event):
        content: str
