from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import VerticalGroup
from textual.widgets import Markdown

from byte.tui import Messages
from byte.tui.schemas import Ask
from byte.tui.widgets.ui.input import Input
from byte.tui.widgets.ui.linting import Linting
from byte.tui.widgets.ui.select import Select
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
        self.current_linting: Linting | None = None

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

    async def mount_select(self, ask: Ask) -> Select:
        select = Select(ask)
        await self.mount(select)
        select.focus()
        return select

    async def mount_input(self, ask: Ask) -> Input:
        input_widget = Input(ask)
        await self.mount(input_widget)
        input_widget.focus()
        return input_widget

    async def mount_panel(self, panel: Messages.CreatePanel) -> Markdown:
        """Mount a generic panel with content from the Panel schema.

        Args:
            panel: Panel schema containing content, title, and border_style

        Returns:
            The mounted Markdown widget
        """
        markdown = Markdown(panel.content)

        if panel.title:
            markdown.border_title = panel.title

        # Map border_style to CSS classes
        style_class_map = {
            "foreground": "border-round",
            "primary": "border-round-primary",
            "secondary": "border-round-secondary",
            "warning": "border-round-warning",
            "error": "border-round-error",
            "success": "border-round-success",
        }

        border_class = style_class_map.get(panel.border_style, "border-round")
        markdown.add_class(border_class)

        await self.mount(markdown)
        return markdown

    async def create_linting(self, file_count: int, command_count: int) -> Linting:
        """Create and mount a new Linting widget.

        Args:
            file_count: Number of files being linted
            command_count: Number of lint commands to execute

        Returns:
            The mounted Linting widget
        """
        linting = Linting()
        await self.mount(linting)
        linting.start_linting(file_count, command_count)
        self.current_linting = linting
        return linting

    async def update_linting_progress(self, current_file: str, completed: int, total: int) -> None:
        """Update progress on the current Linting widget.

        Args:
            current_file: Name of file currently being linted
            completed: Number of files completed
            total: Total number of files
        """
        if self.current_linting is not None:
            self.current_linting.update_progress(current_file, completed, total)

    async def complete_linting(self, total_files: int, failed_files: int, success: bool) -> None:
        """Complete the linting operation on the current Linting widget.

        Args:
            total_files: Total files processed
            failed_files: Number of files with lint errors
            success: Whether all lints passed (no errors)
        """
        if self.current_linting is not None:
            self.current_linting.complete_linting(total_files, failed_files, success)
            self.current_linting = None


# async def add_tool_call(self, tool_data: dict):
#     await self.mount(ToolCallWidget(tool_data))
