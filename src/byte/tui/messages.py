import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from textual.message import Message
from textual.widget import Widget

from byte.tui.schemas import Answer as AnswerSchema, AnswerCancelled

if TYPE_CHECKING:
    pass


class Messages:
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
    class Notify(Message):
        content: str
        style: Literal["default", "warning", "success", "error"] = "default"
        duration: float | None = None

    @dataclass
    class Answer(Message):
        """User selected a response to a question.

        Args:
            answer: The Answer object containing the user's selection.
        """

        answer: AnswerSchema | list[AnswerSchema] | AnswerCancelled

    @dataclass
    class CommandExecutionStarted(Message):
        pass

    @dataclass
    class CommandExecutionCompleted(Message):
        pass

    @dataclass
    class AddHeading(Message):
        heading: str
        classes: str = "text-muted"

    @dataclass
    class ResponseStarted(Message):
        pass

    @dataclass
    class ResponseChunk(Message):
        chunk: str

    @dataclass
    class ResponseComplete(Message):
        pass

    @dataclass
    class CreatePanel(Message):
        """A generic panel for displaying content in the TUI."""

        content: str
        title: str | None = None
        border_style: Literal["foreground", "primary", "secondary", "warning", "error", "success"] = "foreground"

    @dataclass
    class UpdateAnalytics(Message):
        tokens_sent: int
        tokens_received: int
        message_cost: float
        session_cost: float
        memory_percent: float

    @dataclass
    class UpdateFiles(Message):
        editable: int
        read_only: int

    @dataclass
    class LintStarted(Message):
        """Linting operation has started.

        Args:
            file_count: Number of files being linted
            command_count: Number of lint commands to execute
        """

        file_count: int
        command_count: int

    @dataclass
    class LintCompleted(Message):
        """Linting operation has completed.

        Args:
            total_files: Total files processed
            failed_files: Number of files with lint errors
            success: Whether all lints passed (no errors)
        """

        total_files: int
        failed_files: int
        success: bool

    @dataclass
    class LintProgress(Message):
        """Progress update during linting.

        Args:
            current_file: Name of file currently being linted
            completed: Number of files completed
            total: Total number of files
        """

        current_file: str
        completed: int
        total: int

    @dataclass
    class PromptUser(Message):
        """Request user input through an interactive prompt."""

        question: str
        result_future: asyncio.Future[AnswerSchema | list[AnswerSchema] | str | AnswerCancelled]
        prompt_type: Literal["select", "text", "multiselect"] = "text"
        options: list[AnswerSchema] | None = None

    @dataclass
    class LoadingIndicatorShow(Message):
        """Show the loading indicator with an optional message.

        Args:
            message: Optional message to display with the loading indicator
        """

        message: str = "Thinking"

    @dataclass
    class LoadingIndicatorHide(Message):
        """Hide the loading indicator."""

        pass
