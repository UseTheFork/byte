from __future__ import annotations

from textual.app import RenderResult
from textual.content import Content
from textual.widgets import Static


class ByteBug(Static):
    """Display the Byte bug indicator."""

    DEFAULT_CSS = """
    ByteBug {
        width: 3;
        padding-right: 1;
    }
    """

    def render(self) -> RenderResult:
        """Render the Byte bug indicator."""
        return Content.from_markup("[$primary]▌[/][$secondary]▌[/]")
