import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Literal

from textual.message import Message
from textual.notifications import SeverityLevel
from textual.widget import Widget

from byte.tui.schemas import Answer as AnswerSchema, AnswerCancelled
from byte.tui.widgets.prompt.status_bar import StatusState

if TYPE_CHECKING:
    pass


class Status(Enum):
    """Status enum for operations across Messages."""

    PENDING = "pending"
    RUNNING = "running"
    CANCELLED = "cancelled"
    ERROR = "error"
    SUCCESS = "success"


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
        interrupted: bool = False

    # TODO: Do we need this?
    @dataclass
    class UserInputChanged(Message):
        value: str

    @dataclass
    class Notify(Message):
        content: str
        style: SeverityLevel = "information"
        duration: float = 3

    @dataclass
    class Answer(Message):
        """User selected a response to a question.

        Args:
            answer: The Answer object containing the user's selection.
        """

        answer: AnswerSchema | list[AnswerSchema] | AnswerCancelled
        panel_id: str | None = None

    @dataclass
    class CommandExecutionStarted(Message):
        panel_id: str | None = None

    @dataclass
    class CommandExecutionCompleted(Message):
        panel_id: str | None = None

    @dataclass
    class AddUserInput(Message):
        body: str
        command: str | None = None
        panel_id: str | None = None

    @dataclass
    class CreateHeading(Message):
        heading: str
        classes: str = "text-muted"
        panel_id: str | None = None

    @dataclass
    class AddStaticMarkdown(Message):
        content: str = ""
        panel_id: str | None = None

    @dataclass
    class Response(Message):
        status: Status = Status.PENDING
        chunk: str | None = None
        with_indicator: bool | str | None = None
        panel_id: str | None = None

    @dataclass
    class ToolResponse(Message):
        tool_id: str
        status: Status = Status.PENDING
        chunk: str | None = None
        with_indicator: bool | str | None = None
        tool_name: str | None = None
        panel_id: str | None = None

    @dataclass
    class CreatePanel(Message):
        """A generic panel for displaying content in the TUI."""

        content: str
        title: str | None = None
        border_style: Literal["foreground", "primary", "secondary", "warning", "error", "success"] = "foreground"
        panel_id: str | None = None

    @dataclass
    class UpdateAnalytics(Message):
        tokens_sent: int
        tokens_received: int
        message_cost: float
        session_cost: float
        memory_percent: float

    @dataclass
    class UpdateContext(Message):
        context_count: int

    @dataclass
    class UpdateFiles(Message):
        editable: int
        read_only: int

    @dataclass
    class PromptUser(Message):
        """Request user input through an interactive prompt."""

        question: str
        result_future: asyncio.Future[AnswerSchema | list[AnswerSchema] | str | AnswerCancelled]
        prompt_type: Literal["select", "text", "multiselect"] = "text"
        options: list[AnswerSchema] | None = None
        panel_id: str | None = None

    @dataclass
    class Status(Message):
        """ """

        state: StatusState = "default"
        message: str | None = None

    @dataclass
    class ToolCall(Message):
        """Tool call execution message.

        Args:
            name: Name of the tool being called
            args: Arguments passed to the tool
            panel_id: Optional panel identifier for UI routing
        """

        name: str
        args: dict | None = None
        panel_id: str | None = None

    @dataclass
    class Lint(Message):
        """Unified linting operation message with status-based fields.

        Args:
            status: Current status of the linting operation
            total_commands: Total number of command executions (used on PENDING)
            current_file: Name of file currently being linted (used on RUNNING)
            completed: Number of files completed (used on RUNNING)
            total: Total number of files (used on RUNNING)
            total_files: Total files processed (used on SUCCESS)
            failed_files: Number of files with lint errors (used on SUCCESS)
            success: Whether all lints passed (used on SUCCESS)
            panel_id: Optional panel identifier for UI routing
        """

        status: Status = Status.PENDING
        total_commands: int = 0
        current_file: str | None = None
        completed: int = 0
        total: int = 0
        total_files: int = 0
        failed_files: int = 0
        success: bool = True
        panel_id: str | None = None

    @dataclass
    class LintResults(Message):
        """Display lint results message.

        Args:
            content: Formatted markdown content with lint results
            total_issues: Total number of lint issues found
            panel_id: Optional panel identifier for UI routing
        """

        content: str
        total_issues: int
        panel_id: str | None = None

    @dataclass
    class Clear(Message):
        pass
