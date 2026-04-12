from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.reactive import reactive
from textual.widgets import Rule, Static

from byte.tui.widgets.ui.byte_bug import ByteBug


class TextRule(HorizontalGroup):
    """A horizontal rule with text on the left side.

    Example:
        Analytics ───────────────────
    """

    DEFAULT_CSS = """
    TextRule {
        height: 1;
        width: 1fr;
        margin-bottom: 1;
        & Static { 
            width: auto;
            padding-right: 1;
        }
        & Rule { 
            width: 1fr;
        }
    }
    """

    text = reactive("", recompose=True)

    def __init__(
        self,
        text: str = "",
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
        self.text = text

    def compose(self) -> ComposeResult:
        header = Static(self.text)
        yield ByteBug()
        yield header
        yield Rule()
