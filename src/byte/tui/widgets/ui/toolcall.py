from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import VerticalGroup
from textual.widgets import Label

if TYPE_CHECKING:
    from byte.tui import ByteTUI


class ToolCall(VerticalGroup):
    """A widget that displays tool call information."""

    DEFAULT_CSS = """
    ToolCall {
        height: auto;
        background: transparent;
        
        & Label {
            height: auto;
            width: 100%;
        }
    }
    """

    app: ByteTUI

    def __init__(
        self,
        name: str,
        args: dict | None = None,
        id: str | None = None,
        classes: str = "border-round-secondary",
        disabled: bool = False,
    ) -> None:
        super().__init__(
            name=None,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.tool_name = name
        self.tool_args = args or {}

    def compose(self) -> ComposeResult:
        # Display tool name
        yield Label(f"{self.tool_name}()")

        # Display arguments if any
        if self.tool_args:
            for key, value in self.tool_args.items():
                yield Label(f" ╰─ {key}: `{value}`")
