from typing import TYPE_CHECKING

from textual import containers
from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.reactive import reactive
from textual.widgets import Label, ProgressBar

if TYPE_CHECKING:
    pass


class AgentInfo(Label):
    pass


class ModeInfo(Label):
    pass


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

    def compose(self) -> ComposeResult:
        with HorizontalGroup():
            yield Label("Memory Used", classes="px-1 w-auto")
            yield ProgressBar(total=100, show_eta=False, classes="w-50", id="memory-progress")
        with containers.HorizontalGroup(classes="w-full"):
            yield ModeInfo(self.tokens_used, classes="px-1 w-50 text-left", id="tokens-label")
            yield ModeInfo(self.cost, classes="px-1 w-50 text-right", id="cost-label")

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
        self.query_one("#tokens-label", ModeInfo).update(self.tokens_used)
        self.query_one("#cost-label", ModeInfo).update(self.cost)

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
