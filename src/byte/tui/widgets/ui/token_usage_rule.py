from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.reactive import reactive
from textual.widgets import Rule, Static


class TokenUsageRule(HorizontalGroup, can_focus=False):
    """A horizontal rule with token usage text on the right side.

    Example:
        ─────────────────── Tokens: 1,234 in / 567 out · Cost: $0.0042
    """

    DEFAULT_CSS = """
    TokenUsageRule {
        height: 1;
        width: 1fr;
        margin-bottom: 1;
        padding-right: 1;
        & Rule { 
            width: 1fr;
        }
        & Static { 
            width: auto;
            padding-left: 1;
        }
    }
    """

    text = reactive("")

    def __init__(
        self,
        text: str = "",
        *,
        input_tokens: int = 0,
        output_tokens: int = 0,
        input_cache_read: int = 0,
        input_cache_creation: int = 0,
        cost: float = 0.0,
        max_input_tokens: int = 0,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            classes=classes or "text-muted",
            disabled=disabled,
        )
        self.text = text
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.input_cache_read = input_cache_read
        self.input_cache_creation = input_cache_creation
        self.cost = cost
        self.max_input_tokens = max_input_tokens

    def validate_text(self, text: str) -> str:
        return text.strip()

    def compose(self) -> ComposeResult:
        yield Rule()
        summary_text = Static(self.text)
        yield summary_text
