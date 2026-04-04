from dataclasses import dataclass
from typing import TYPE_CHECKING

from textual.widget import Widget

from byte.event import Event

if TYPE_CHECKING:
    from byte.tui.schemas import ChatMessage


# Sub events that specifically have to do with the TUI
class TuiEvents:
    @dataclass
    class PromptSuggestion(Event):
        suggestion: str

    @dataclass
    class Dismiss(Event):
        widget: Widget

        @property
        def control(self) -> Widget:
            return self.widget

    @dataclass
    class UserInputSubmitted(Event):
        body: str
        auto_complete: bool = False

    @dataclass
    class UserInputChanged(Event):
        value: str

    @dataclass
    class CommandExecutionStarted(Event):
        command_name: str

    @dataclass
    class WorkflowStarted(Event):
        pass

    @dataclass
    class AgentResponseStarted(Event):
        agent: str

    @dataclass
    class AgentResponseStreamChunk(Event):
        chunk: dict

    @dataclass
    class AgentResponseComplete(Event):
        pass

    @dataclass
    class WorkflowComplete(Event):
        pass

    @dataclass
    class AIMessageChunk(Event):
        chunk: str

    @dataclass
    class AgentResponseFailed(Event):
        """Sent when the agent fails to respond e.g. cant connect.
        Can be used to reset UI state."""

        last_message: ChatMessage

    @dataclass
    class NewUserMessage(Event):
        content: str
