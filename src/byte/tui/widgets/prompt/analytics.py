from typing import TYPE_CHECKING

from textual import containers
from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.reactive import reactive, var
from textual.widgets import Label, ProgressBar

if TYPE_CHECKING:
    pass


class TokensInfo(Label):
    tokens_used: reactive[str] = reactive("")

    def watch_tokens_used(self, tokens_used: str) -> None:
        """Update the label when tokens_used changes."""
        self.update(tokens_used)


class CostInfo(Label):
    cost: reactive[str] = reactive("")

    def watch_cost(self, cost: str) -> None:
        """Update the label when cost changes."""
        self.update(cost)


class FileInfo(Label):
    editable: reactive[int] = reactive(0)
    read_only: reactive[int] = reactive(0)

    def _format_file_info(self) -> str:
        """Format the file info display text."""
        return f"Files: {self.editable} E | {self.read_only} RO"

    def watch_editable(self, editable: int) -> None:
        """Update the label when editable changes."""
        self.update(self._format_file_info())

    def watch_read_only(self, read_only: int) -> None:
        """Update the label when read_only changes."""
        self.update(self._format_file_info())


class Analytics(containers.VerticalGroup):
    BORDER_TITLE = "Analytics"

    COMPONENT_CLASSES = [
        "h-auto",
        "w-full",
        "pl-1",
        "pr-1",
    ]

    DEFAULT_CSS = """
    Analytics {
        min-width: 12;
        max-width: 1fr;
        border: round $secondary 30%;
    }
    """

    tokens_used: reactive[str] = reactive("Tokens: 0 sent, 0 received")
    cost: reactive[str] = reactive("Cost: $0.00 message, $0.00 session.")
    memory_used: reactive[str] = reactive("0%")
    memory_percent: reactive[float] = reactive(0.0)

    files_read_only: var[int] = var(0)
    files_editable: reactive[int] = reactive(0)
    files_read_only_count: reactive[int] = reactive(0)

    def compose(self) -> ComposeResult:
        with HorizontalGroup():
            yield Label("Memory Used", classes="px-1 w-auto")
            yield ProgressBar(total=100, show_eta=False, classes="w-50", id="memory-progress")
            yield FileInfo(classes="px-1 w-auto text-right").data_bind(
                editable=Analytics.files_editable, read_only=Analytics.files_read_only_count
            )
        with containers.HorizontalGroup(classes="w-full"):
            yield TokensInfo(self.tokens_used, classes="px-1 w-50 text-left").data_bind(
                tokens_used=Analytics.tokens_used
            )
            yield CostInfo(self.cost, classes="px-1 w-50 text-right").data_bind(cost=Analytics.cost)

    def update_analytics(
        self,
        tokens_sent: int,
        tokens_received: int,
        message_cost: float,
        session_cost: float,
        memory_percent: float,
    ) -> None:
        """Update analytics display with current usage statistics.

        Args:
            tokens_sent: Number of tokens sent in the last message.
            tokens_received: Number of tokens received in the last message.
            message_cost: Cost of the last message in dollars.
            session_cost: Total cost of the session in dollars.
            memory_percent: Percentage of memory used (0-100).
        """
        self.tokens_used = f"Tokens: {self.humanizer(tokens_sent)} sent, {self.humanizer(tokens_received)} received"
        self.cost = f"Cost: ${message_cost:.2f} message, ${session_cost:.2f} session."
        self.memory_used = f"{memory_percent:.1f}%"
        self.memory_percent = memory_percent

        # Update the progress bar
        progress_bar = self.query_one("#memory-progress", ProgressBar)
        progress_bar.update(progress=memory_percent)

        # # Update the labels
        # TokensInfo and CostInfo update automatically via data_bind

    def humanizer(self, number: int | float) -> str:
        divisor = 1
        for suffix in ("K", "M", "B", "T"):
            divisor *= 1000
            max_allowed = divisor * 1000
            quotient, remainder = divmod(number, divisor)
            if number > max_allowed:
                continue
            if quotient:
                break
            return str(number)
        if remaining := (remainder and round(remainder / divisor, 1)):
            quotient += remaining
        return f"{quotient}{suffix}"
