import asyncio

from partial_json_parser import OBJ, loads
from rich.console import RenderableType
from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget


class ToolCallStream:
    """An object to manage streaming tool call arguments.

    This will accumulate argument fragments if they can't be rendered fast enough.
    """

    def __init__(self, tool_call_display: ToolCall) -> None:
        """
        Args:
            tool_call_display: ToolCallDisplay widget to update.
        """
        self.tool_call_display = tool_call_display
        self._task: asyncio.Task | None = None
        self._new_markup = asyncio.Event()
        self._pending: list[str] = []
        self._stopped = False

    async def _run(self) -> None:
        """Run a task to append argument fragments when available."""
        try:
            while await self._new_markup.wait():
                new_args = "".join(self._pending)
                self._pending.clear()
                self._new_markup.clear()
                await asyncio.shield(self.tool_call_display.append(new_args))
        except asyncio.CancelledError:
            # Task has been cancelled, add any outstanding arguments
            pass

        new_args = "".join(self._pending)
        if new_args:
            await self.tool_call_display.append(new_args)

    def start(self) -> None:
        """Start the updater running in the background.

        No need to call this, if the object was created by ToolCallDisplay.get_stream.
        """
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
        """Append or enqueue an argument fragment.

        Args:
            fragment: A string to append at the end of the arguments.
        """
        if self._stopped:
            raise RuntimeError("Can't write to the stream after it has stopped.")
        if not fragment:
            # Nothing to do for empty strings.
            return
        # Append the new fragment, and set an event to tell the _run loop to wake up
        self._pending.append(fragment)
        self._new_markup.set()
        # Allow the task to wake up and actually display the new arguments
        await asyncio.sleep(0)


class ToolCall(Widget, can_focus=False):
    """A widget that displays tool call information with streaming support."""

    raw_args = reactive("")

    DEFAULT_CSS = """
    ToolCall {
        height: auto;
        background: transparent;
        border-top: round $secondary;
        
        & Label {
            height: auto;
            width: 100%;
        }
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
        self.border_title = f"{self.tool_name}()"
        self.raw_args = ""

    def render(self) -> RenderableType:
        """Render the tool call display."""
        try:
            parsed = loads(self.raw_args, OBJ)
        except Exception:
            parsed = None

        # Build the output text
        output = Text("")

        # If we have a valid parsed dictionary, display its contents
        if parsed is not None and isinstance(parsed, dict) and parsed:
            for key, value in parsed.items():
                output.append(f"\n╰─ {key}: {value}")
        elif self.raw_args:
            # If parsing failed but we have raw args, show them
            output.append(f"\n{self.raw_args}")

        return output

    async def append(self, fragment: str) -> None:
        """Append a fragment to the raw arguments."""
        self.raw_args = self.raw_args + fragment
        self.refresh(layout=True)

    @classmethod
    def get_stream(cls, widget: ToolCall) -> ToolCallStream:
        """Get a stream for writing tool call arguments to this widget."""
        stream = ToolCallStream(widget)
        stream.start()
        return stream
