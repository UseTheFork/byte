from typing import TYPE_CHECKING

from textual import getters
from textual.containers import VerticalGroup
from textual.css.query import NoMatches
from textual.widgets import Markdown

from byte.tui import Messages
from byte.tui.schemas import Ask
from byte.tui.widgets.ui.human_message import HumanMessage
from byte.tui.widgets.ui.linting import Linting
from byte.tui.widgets.ui.loading_indicator import LoadingIndicator
from byte.tui.widgets.ui.multi_select import MultiSelect
from byte.tui.widgets.ui.reasoning_markdown import ReasoningMarkdown
from byte.tui.widgets.ui.select import Select
from byte.tui.widgets.ui.selectable_markdown import SelectableMarkdown
from byte.tui.widgets.ui.text_input import TextInput
from byte.tui.widgets.ui.text_rule import TextRule
from byte.tui.widgets.ui.token_usage_rule import TokenUsageRule
from byte.tui.widgets.ui.tool_call import ToolCall

if TYPE_CHECKING:
    from byte.tui import ByteTUI


class ResponsePanel(VerticalGroup):
    app: ByteTUI
    loading_indicator = getters.query_one(LoadingIndicator)

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
        self.streams = {}
        self.current_linting: Linting | None = None
        self.total_cost: float = 0.0
        self.total_input_tokens: int = 0
        self.total_output_tokens: int = 0
        self.turn_count: int = 0
        self.aggregate_usage: TokenUsageRule | None = None

    async def add_user_message(self, event: Messages.AddUserInput):
        await self.mount(HumanMessage(f"/{event.command} {event.body}"))

    async def add_heading(self, event: Messages.CreateHeading):
        await self.mount(TextRule(event.heading, classes=event.classes))

    async def add_static_markdown(self, content: str = "", border_title: str = ""):
        markdown = SelectableMarkdown(content, border_title=border_title)
        await self.mount(markdown)
        return markdown

    async def start_markdown_stream(self, border_title: str = ""):
        markdown_widget = await self.add_static_markdown("", border_title)
        self.current_stream = SelectableMarkdown.get_stream(markdown_widget)
        return self.current_stream

    async def add_markdown_chunk(self, chunk: str):
        if self.current_stream is None:
            await self.start_markdown_stream()

        assert self.current_stream is not None, "start_markdown_stream() must be called before add_markdown_chunk()"
        await self.current_stream.write(chunk)

    async def end_markdown_stream(self):
        if self.current_stream is None:
            return

        await self.current_stream.stop()

    async def start_reasoning_stream(self, border_title: str = "Reasoning") -> None:
        import time

        reasoning_widget = ReasoningMarkdown(border_title=border_title)
        reasoning_widget.start_time = time.time()
        await self.mount(reasoning_widget)
        self.current_reasoning_widget = reasoning_widget
        self.current_reasoning_stream = ReasoningMarkdown.get_stream(reasoning_widget)

    async def add_reasoning_chunk(self, chunk: str):
        if not hasattr(self, "current_reasoning_stream") or self.current_reasoning_stream is None:
            await self.start_reasoning_stream()

        assert self.current_reasoning_stream is not None, (
            "start_reasoning_stream() must be called before add_reasoning_chunk()"
        )
        await self.current_reasoning_stream.write(chunk)

    async def end_reasoning_stream(self):
        if not hasattr(self, "current_reasoning_stream") or self.current_reasoning_stream is None:
            return

        await self.current_reasoning_stream.stop()
        if hasattr(self, "current_reasoning_widget") and self.current_reasoning_widget is not None:
            self.current_reasoning_widget.complete()
            self.current_reasoning_widget = None

    async def start_tool_stream(
        self,
        tool_name: str,
        tool_id: str,
    ):
        tool_widget = ToolCall(tool_name=tool_name, id=f"{tool_id}")
        await self.mount(tool_widget)
        self.streams[tool_id] = ToolCall.get_stream(tool_widget)
        return self.streams[tool_id]

    async def add_tool_chunk(self, tool_id: str, chunk: str):
        assert self.streams[tool_id] is not None, "start_tool_stream() must be called before add_tool_chunk()"
        await self.streams[tool_id].write(chunk)

    async def end_tool_stream(self, tool_id: str):
        if self.streams[tool_id] is None:
            return

        await self.streams[tool_id].stop()

    async def mount_select(self, ask: Ask) -> Select:
        select = Select(ask)
        await self.mount(select)
        select.focus()
        return select

    async def mount_multi_select(self, ask: Ask) -> MultiSelect:
        multi_select = MultiSelect(ask)
        await self.mount(multi_select)
        multi_select.focus()
        return multi_select

    async def mount_input(self, ask: Ask) -> TextInput:
        input_widget = TextInput(ask)
        await self.mount(input_widget)
        input_widget.focus()
        return input_widget

    async def mount_panel(self, panel: Messages.CreatePanel) -> Markdown:
        """Mount a generic panel."""
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

    async def create_linting(self, event: Messages.Lint) -> Linting:
        """Create and mount a linting widget."""
        linting = Linting()
        await self.mount(linting)
        await linting.start_linting(event.total_commands)
        self.current_linting = linting
        return linting

    async def update_linting_progress(self, current_file: str, completed: int, total: int) -> None:
        """Update linting progress."""
        if self.current_linting is not None:
            await self.current_linting.update_progress(current_file, completed, total)

    async def complete_linting(self, total_files: int, failed_files: int, success: bool) -> None:
        """Complete the linting operation."""
        if self.current_linting is not None:
            await self.current_linting.complete_linting(total_files, failed_files, success)

    async def complete_toolcall(self, event: Messages.ToolCall):
        try:
            tool_call = self.query_one(f"#{event.tool_id}", ToolCall)
            tool_call.complete(status=event.status, content=event.content)
        except NoMatches:
            self.app.byte["log"].info(event)

    async def update_aggregate_usage(self, event: Messages.CreateTokenUsage) -> None:
        """Update the aggregate token usage widget."""
        self.total_cost += event.cost
        self.total_input_tokens += event.input_tokens
        self.total_output_tokens += event.output_tokens
        self.turn_count += 1

        summary_text = (
            f"Total: {self.total_input_tokens:,} in / {self.total_output_tokens:,} out "
            f"· Cost: ${self.total_cost:.2f} ({self.turn_count} turns)"
        )

        if self.aggregate_usage is None:
            self.aggregate_usage = TokenUsageRule(text=summary_text, classes="text-secondary-50")
            await self.mount(self.aggregate_usage)
        else:
            # Remove from DOM and re-mount at the bottom to ensure it stays last
            await self.aggregate_usage.remove()
            await self.mount(self.aggregate_usage)
            # Update the text via the reactive property
            self.aggregate_usage.text = summary_text
