from __future__ import annotations

from textual.app import RenderResult
from textual.widget import Widget


class Bootbox(Widget, can_focus=False):
    DEFAULT_CSS = """
    Bootbox {
        height: auto;
        width: 100%;
        min-width: 12;
        max-width: 1fr;
        margin: 0 1;
        padding: 0 2;
        border: round $primary;
    }
    """

    def __init__(
        self,
        message: str,
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
        self.message = message

    def render(self) -> RenderResult:
        return self.message
