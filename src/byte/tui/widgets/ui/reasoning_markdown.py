import asyncio

from rich.console import RenderableType
from rich.markdown import Markdown
from rich.text import Text
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Collapsible

from byte.tui import Messages
from byte.tui.constants import ANGLE_DOWN, ANGLE_RIGHT


class ReasoningContent(Widget, can_focus=False):
    """Display streaming reasoning content."""

    DEFAULT_CSS = """
    ReasoningContent {
        height: auto;

        & Label {
            height: auto;
            width: 100%;
        }
    }
    """

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
        self.raw_content = ""

    def render(self) -> RenderableType:
        """Render the reasoning content as markdown."""
        if not self.raw_content:
            return Text("")

        return Markdown(self.raw_content)

    async def append(self, fragment: str) -> None:
        """Append a fragment to raw content."""
        self.raw_content = self.raw_content + fragment
        self.refresh(layout=True)
        await asyncio.sleep(0)


class MarkdownStream:
    """Manage streaming markdown."""

    def __init__(self, reasoning_content: ReasoningContent) -> None:
        self.reasoning_content = reasoning_content
        self._task: asyncio.Task | None = None
        self._new_markup = asyncio.Event()
        self._pending: list[str] = []
        self._stopped = False

    async def _run(self) -> None:
        """Run a task to append markdown fragments when available."""
        try:
            while await self._new_markup.wait():
                new_markdown = "".join(self._pending)
                self._pending.clear()
                self._new_markup.clear()
                await asyncio.shield(self.reasoning_content.append(new_markdown))
        except asyncio.CancelledError:
            # Task has been cancelled, add any outstanding markdown
            pass

        new_markdown = "".join(self._pending)
        if new_markdown:
            await self.reasoning_content.append(new_markdown)

    def start(self) -> None:
        """Start the updater running in the background."""
        if self._task is None:
            self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        """Stop the stream and await its finish."""
        if self._task is not None:
            self._task.cancel()
            await self._task
            self._task = None
            self._stopped = True

    async def write(self, markdown_fragment: str) -> None:
        """Append or enqueue a markdown fragment."""
        if self._stopped:
            raise RuntimeError("Can't write to the stream after it has stopped.")
        if not markdown_fragment:
            # Nothing to do for empty strings.
            return

        self.reasoning_content.post_message(Messages.TokenReceived(markdown_fragment))
        # Append the new fragment, and set an event to tell the _run loop to wake up
        self._pending.append(markdown_fragment)
        self._new_markup.set()
        # Allow the task to wake up and actually display the new markdown
        await asyncio.sleep(0)


class ReasoningCollapsible(Collapsible):
    DEFAULT_CSS = """
    ReasoningCollapsible {
            width: 1fr;
            height: auto;
            background: transparent;
            border-top: hkey $background;
            padding-bottom: 1;

            &:focus-within {
                background-tint: $foreground 5%;
            }

            &.-collapsed > Contents {
                display: none;
            }
    }
    """


class ReasoningMarkdown(Widget, can_focus=False):
    """Display streaming reasoning content with collapsible container."""

    DEFAULT_CSS = """
    ReasoningMarkdown {
        height: auto;
        background: transparent;
        border-top: round $primary 50%;
        margin-bottom: 1;
    }
    """

    def __init__(
        self,
        border_title: str = "Reasoning",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialize a reasoning markdown widget."""
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.border_title = f" {border_title} ( Thinking ) "

    def compose(self) -> ComposeResult:
        """Compose the reasoning widget with collapsible container."""
        with ReasoningCollapsible(
            title="Reasoning", collapsed=False, collapsed_symbol=ANGLE_RIGHT, expanded_symbol=ANGLE_DOWN
        ):
            yield ReasoningContent()

    def complete(self) -> None:
        """Collapse the reasoning section."""
        collapsible = self.query_one(ReasoningCollapsible)
        collapsible.collapsed = True

    @classmethod
    def get_stream(cls, widget: ReasoningMarkdown) -> MarkdownStream:
        """Create and start a MarkdownStream for the widget."""
        reasoning_content = widget.query_one(ReasoningContent)
        stream = MarkdownStream(reasoning_content)
        stream.start()
        return stream
