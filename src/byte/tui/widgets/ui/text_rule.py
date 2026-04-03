from __future__ import annotations

from rich.console import RenderableType
from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget


class TextRule(Widget, can_focus=False):
    """A horizontal rule with text on the left side.

    Example:
        Analytics ───────────────────
    """

    DEFAULT_CSS = """
    TextRule {
        height: 1;
        width: 100%;
        color: $text-muted;
    }
    """

    text = reactive("")

    def __init__(
        self,
        rule_char: str = "─",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.rule_char = rule_char

    def render(self) -> RenderableType:
        """Render the text followed by a horizontal rule."""
        width = self.size.width
        text_length = len(self.text)

        if text_length >= width:
            return Text(self.text[:width])

        # Add space after text if text is provided
        if self.text:
            rule_length = width - text_length - 1
            return Text(f"{self.text} {self.rule_char * rule_length}")
        else:
            return Text(self.rule_char * width)
