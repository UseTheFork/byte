from __future__ import annotations

from textual.app import RenderResult
from textual.content import Content
from textual.widgets import Static


class ByteBug(Static):
    """ """

    DEFAULT_CSS = """
    ByteBug {
        width: 3;
        padding-right: 1;
    }
    """

    def render(self) -> RenderResult:
        """Render the text followed by a horizontal rule."""
        return Content.from_markup("[$primary]▌[/][$secondary]▌[/]")
