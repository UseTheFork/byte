import asyncio
import re
from typing import TYPE_CHECKING

from rich.console import RenderableType
from rich.markdown import Markdown
from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget

from byte.tui.messages import Messages

if TYPE_CHECKING:
    from byte.tui import ByteTUI


class ToolArgs(Widget, can_focus=False):
    """Display streaming tool call arguments with phase information."""

    app: ByteTUI

    DEFAULT_CSS = """
    ToolArgs {
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
        self.raw_args = ""

    def render(self) -> RenderableType:
        """Render phase information extracted from raw arguments."""
        if not self.raw_args:
            return Text("")

        output = Text("")

        # Extract phase_id using regex
        phase_id_match = re.search(r'"phase_id"\s*:\s*"([^"]*)"', self.raw_args)
        phase_id = phase_id_match.group(1) if phase_id_match else None

        # Extract phase_status using regex
        phase_status_match = re.search(r'"phase_status"\s*:\s*"([^"]*)"', self.raw_args)
        phase_status = phase_status_match.group(1) if phase_status_match else None

        # Post phase update message if we found either value
        if phase_id or phase_status:
            self.post_message(Messages.PhaseUpdated(phase_id, phase_status))

        # Display phase information
        if phase_id:
            output.append(f"\n   phase_id: {phase_id}")
        if phase_status:
            output.append(f"\n   phase_status: {phase_status}")

        return output

    async def append(self, fragment: str) -> None:
        """Append a fragment to raw arguments using snapshot semantics."""
        self.raw_args = fragment
        self.refresh(layout=True)
        await asyncio.sleep(0)


class ToolCallStream:
    """Manage streaming tool call arguments with throttling."""

    THROTTLE_MS: int = 40  # Throttle UI updates to ~40ms (25 updates/sec max)

    def __init__(self, tool_call_display: ToolArgs) -> None:
        self.tool_call_display = tool_call_display
        self._task: asyncio.Task | None = None
        self._new_markup = asyncio.Event()
        self._latest_chunk: str = ""
        self._stopped = False
        self._last_update_time: float = 0.0

    async def _run(self) -> None:
        """Run a task to append argument chunks with throttling."""
        try:
            while await self._new_markup.wait():
                self._new_markup.clear()

                # Throttle updates: only refresh if enough time has passed
                import time

                current_time = time.time()
                elapsed_ms = (current_time - self._last_update_time) * 1000

                if elapsed_ms >= self.THROTTLE_MS:
                    # Enough time has passed, update immediately
                    await asyncio.shield(self.tool_call_display.append(self._latest_chunk))
                    self._last_update_time = current_time
                else:
                    # Not enough time; sleep and retry
                    sleep_time = (self.THROTTLE_MS - elapsed_ms) / 1000
                    await asyncio.sleep(sleep_time)
                    await asyncio.shield(self.tool_call_display.append(self._latest_chunk))
                    self._last_update_time = time.time()
        except asyncio.CancelledError:
            # Task has been cancelled, add any outstanding chunk
            pass

        # Flush final chunk on stop
        if self._latest_chunk:
            await self.tool_call_display.append(self._latest_chunk)

    def start(self) -> None:
        """Start the updater in the background."""
        if self._task is None:
            self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        """Stop the stream and await its finish."""
        if self._task is not None:
            self._task.cancel()
            await self._task
            self._task = None
            self._stopped = True

    async def write(self, fragment: str) -> None:
        """Append or enqueue an argument fragment using snapshot semantics."""
        if self._stopped:
            raise RuntimeError("Can't write to the stream after it has stopped.")
        if not fragment:
            # Nothing to do for empty strings.
            return

        self.tool_call_display.post_message(Messages.TokenReceived(fragment))
        # Store the latest chunk snapshot (replaces previous, not appends)
        self._latest_chunk = fragment
        self._new_markup.set()
        # Allow the task to wake up and actually display the new arguments
        await asyncio.sleep(0)


class ToolResult(Widget, can_focus=False):
    """Display the final result of a tool call."""

    DEFAULT_CSS = """
    ToolResult {
        display: none;
        height: auto;
    }
    """

    message = reactive("")

    @property
    def markdown(self) -> Markdown:
        """Return the content as a Rich Markdown object."""
        content = str(self.message)

        return Markdown(content)
        # return Markdown(content, code_theme=self.app.launch_config.message_code_theme)

    def render(self) -> RenderableType:
        """Render the result as Markdown."""
        return self.markdown


class ToolCall(Widget, can_focus=False):
    """Display tool call information with streaming support."""

    raw_args = reactive("")

    DEFAULT_CSS = """
    ToolCall {
        height: auto;
        background: transparent;
        border-top: round $secondary;
        border-bottom: round $secondary;
        margin-bottom: 1;
    }
    """

    def __init__(
        self,
        tool_name: str,
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
        self.tool_name = tool_name
        self.border_title = f" {self.tool_name}() "

    def compose(self) -> ComposeResult:
        """Compose the tool call widget with phase information and result sections."""
        yield ToolArgs()
        yield ToolResult()

    @on(Messages.PhaseUpdated)
    def phase_updated(self, event: Messages.PhaseUpdated) -> None:
        """Update border subtitle with phase information."""
        parts = []
        if event.phase_id:
            parts.append(f"  {event.phase_id}")
        if event.phase_status:
            parts.append(f"{event.phase_status}  ")
        if parts:
            self.border_subtitle = " · ".join(parts)

    def complete(self, status: str = "success", content: str | None = None) -> None:
        """Display the result."""
        result_widget = self.query_one(ToolResult)
        if status == "success":
            pass
        else:
            pass

        result_widget.message = f" {content or status}"
        result_widget.styles.display = "block"

    @classmethod
    def get_stream(cls, widget: ToolCall) -> ToolCallStream:
        """Create and start a ToolCallStream for the widget."""
        tool_args = widget.query_one(ToolArgs)
        stream = ToolCallStream(tool_args)  # Stream targets ToolArgs now
        stream.start()
        return stream
