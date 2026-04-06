from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from byte.event import Event

if TYPE_CHECKING:
    from byte.tui.schemas import ChatMessage


class TuiComponentEvent(Event):
    pass


# Sub events that specifically have to do with the TUI
class TuiComponentEvents:
    @dataclass
    class CommandExecutionStarted(TuiComponentEvent):
        pass

    @dataclass
    class CommandExecutionCompleted(TuiComponentEvent):
        pass

    @dataclass
    class AddHeading(TuiComponentEvent):
        heading: str
        classes: str = "text-muted"

    @dataclass
    class ResponseStarted(TuiComponentEvent):
        pass

    @dataclass
    class ResponseChunk(TuiComponentEvent):
        chunk: str

    @dataclass
    class ResponseComplete(TuiComponentEvent):
        pass

    @dataclass
    class PromptSuggestion(TuiComponentEvent):
        suggestion: str

    @dataclass
    class UserInputSubmitted(TuiComponentEvent):
        body: str
        auto_complete: bool = False

    @dataclass
    class UserInputChanged(TuiComponentEvent):
        value: str

    @dataclass
    class UpdateAnalytics(TuiComponentEvent):
        tokens_sent: int
        tokens_received: int
        message_cost: float
        session_cost: float
        memory_percent: float

    @dataclass
    class UpdateFiles(TuiComponentEvent):
        editable: int
        read_only: int

    @dataclass
    class Notify(TuiComponentEvent):
        content: str
        style: Literal["default", "warning", "success", "error"] = "default"
        duration: float | None = None

    @dataclass
    class AgentResponseFailed(TuiComponentEvent):
        """Sent when the agent fails to respond e.g. cant connect.
        Can be used to reset UI state."""

        last_message: ChatMessage

    @dataclass
    class NewUserMessage(TuiComponentEvent):
        content: str
