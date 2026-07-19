from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.reactive import reactive
from textual.widgets import Rule, Static

from byte.tui.widgets.ui.byte_bug import ByteBug


class TextRule(HorizontalGroup, can_focus=False):
    """Render a horizontal rule with text on the left side."""

    DEFAULT_CSS = """
    TextRule {
        height: 1;
        width: 1fr;
        margin-bottom: 1;
        padding-right: 1;
        & Static {
            width: auto;
            padding-right: 1;
        }
        & Rule {
            width: 1fr;
        }
    }
    """

    text = reactive("")

    def __init__(
        self,
        text: str = "",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialize a text rule widget."""
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.text = text

    def validate_text(self, text: str) -> str:
        """Validate the text by stripping whitespace."""
        return text.strip()

    def compose(self) -> ComposeResult:
        """Compose the widget's child components."""
        header = Static(self.text)
        yield ByteBug()
        yield header
        yield Rule()
