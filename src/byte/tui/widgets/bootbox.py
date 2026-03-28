from __future__ import annotations

from rich.console import RenderableType
from rich.markdown import Markdown
from textual.widget import Widget


class Bootbox(Widget, can_focus=False):
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

    @property
    def markdown(self) -> Markdown:
        """Return the content as a Rich Markdown object."""

        return Markdown("this is a test")
        # return Markdown(content, code_theme=self.app.launch_config.message_code_theme)

    def render(self) -> RenderableType:
        return self.markdown
