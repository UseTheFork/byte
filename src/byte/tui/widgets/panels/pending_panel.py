from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import VerticalGroup
from textual.widgets import Markdown

from byte.tui.widgets.ui.text_rule import TextRule

if TYPE_CHECKING:
    from byte.tui import ByteTUI


class PendingPanel(VerticalGroup):
    app: ByteTUI

    def __init__(
        self,
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
        self.current_stream = None

    async def add_heading(self, heading: str, classes: str = "text-muted"):
        await self.mount(TextRule(heading, classes=classes))

    async def add_static_markdown(self, content: str = ""):
        markdown = Markdown(content)
        await self.mount(markdown)
        return markdown

    async def start_markdown_stream(self):
        markdown_widget = await self.add_static_markdown("")
        self.current_stream = Markdown.get_stream(markdown_widget)
        return self.current_stream

    async def add_markdown_chunk(self, chunk: str):
        assert self.current_stream is not None, "start_markdown_stream() must be called before add_markdown_chunk()"
        await self.current_stream.write(chunk)

    async def end_markdown_stream(self):
        if self.current_stream is None:
            return

        await self.current_stream.stop()

    # async def add_tool_call(self, tool_data: dict):
    #     await self.mount(ToolCallWidget(tool_data))

    # async def add_lint_results(self, results: list):
    #     await self.mount(LintResultsWidget(results))
