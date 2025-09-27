import asyncio
from typing import Dict, Optional

from rich.console import Console
from rich.live import Live
from rich.rule import Rule
from rich.spinner import Spinner
from rich.text import Text

from byte.core.actors.base import Actor
from byte.core.actors.message import Message, MessageType
from byte.core.response.formatters import MarkdownStream


class ReactiveMarkdownStream(MarkdownStream):
    """Enhanced MarkdownStream that works with the actor system"""

    def __init__(self, stream_id: str, update_callback=None):
        super().__init__()
        self.stream_id = stream_id
        self.update_callback = update_callback

    async def update_async(self, text: str, final: bool = False):
        """Async version of update that yields control"""
        # Process all lines at once like the original update method
        lines = self._render_markdown_to_lines(text)

        # Process all lines without chunking
        await self._process_line_chunk(lines, final)

        # Yield control once
        await asyncio.sleep(0)

        if self.update_callback:
            await self.update_callback(self.stream_id, len(lines))

    async def _process_line_chunk(self, lines_chunk, is_final):
        """Process chunk of lines without blocking"""
        if not self._live_started:
            self.live = Live(Text(""), refresh_per_second=20)
            self.live.start()
            self._live_started = True

        # lines_chunk contains ALL lines from accumulated content
        # We need to figure out what's new since last time
        total_lines = len(lines_chunk)
        num_already_printed = len(self.printed)

        if not is_final:
            # Keep some lines in the live window for updates
            stable_lines = max(0, total_lines - self.live_window)
        else:
            # If final, all lines are stable
            stable_lines = total_lines

        # Calculate how many new stable lines to print above live window
        new_stable_count = stable_lines - num_already_printed

        if new_stable_count > 0:
            # Print only the NEW stable lines above the live window
            new_stable_lines = lines_chunk[num_already_printed:stable_lines]
            stable_text = "".join(new_stable_lines)
            if stable_text:
                stable_display = Text.from_ansi(stable_text)
                self.live.console.print(stable_display)

            # Update our record of printed lines
            self.printed = lines_chunk[:stable_lines]

        # Update live window with remaining unstable lines
        if not is_final:
            remaining_lines = lines_chunk[stable_lines:]
            if remaining_lines:
                live_text = "".join(remaining_lines)
                live_display = Text.from_ansi(live_text)
                self.live.update(live_display)

        if is_final and self.live:
            self.live.update(Text(""))
            self.live.stop()
            self.live = None


class RenderingActor(Actor):
    async def boot(self):
        await super().boot()
        self.console = Console()
        self.active_stream: Optional[ReactiveMarkdownStream] = None
        self.current_stream_id: Optional[str] = None
        self.spinner: Optional[Live] = None
        self.accumulated_content: str = ""

        # Track single tool call state with simple Live display
        self.active_tool_calls: Dict[str, dict] = {}  # Single tool call tracking
        self.tool_json_live: Optional[Live] = None

    async def handle_message(self, message: Message):
        if message.type == MessageType.SHUTDOWN:
            await self.stop()
        elif message.type == MessageType.START_STREAM:
            await self._start_stream_render(message.payload)
        elif message.type == MessageType.STREAM_CHUNK:
            await self._handle_chunk(message.payload)
        elif message.type == MessageType.END_STREAM:
            await self._end_stream(message.payload)
        elif message.type == MessageType.CANCEL_STREAM:
            await self._cancel_stream(message.payload)
        elif message.type == MessageType.TOOL_START:
            await self._show_tool_usage(message.payload)
        elif message.type == MessageType.TOOL_END:
            await self._hide_tool_usage(message.payload)
        elif message.type == MessageType.STREAM_ERROR:
            await self._handle_stream_error(message.payload)

    async def _start_stream_render(self, payload):
        stream_id = payload["stream_id"]
        metadata = payload["metadata"]

        # Clean up any existing stream
        if self.active_stream:
            await self.active_stream.update_async("", final=True)
        if self.spinner:
            self.spinner.stop()

        self.current_stream_id = stream_id
        self.accumulated_content = ""  # Reset accumulated content for new stream

        # Show initial UI elements
        self.console.print()

        if metadata.stream_type == "agent":
            self.console.print(Rule("Agent", align="left"))

            # Start with spinner
            spinner = Spinner("dots", text="Thinking...")
            self.spinner = Live(
                spinner, console=self.console, transient=True, refresh_per_second=20
            )
            self.spinner.start()

        # Create markdown stream
        self.active_stream = ReactiveMarkdownStream(
            stream_id, update_callback=self._on_stream_update
        )

    async def _handle_chunk(self, payload):
        stream_id = payload["stream_id"]
        chunk = payload["chunk"]

        # log.info(payload)

        # Stop spinner if it's running
        if self.spinner:
            self.spinner.stop()
            self.spinner = None

        # Create new stream if it doesn't exist (after tool usage)
        if not self.active_stream or self.current_stream_id != stream_id:
            self.current_stream_id = stream_id
            self.accumulated_content = ""  # Reset for new stream
            self.active_stream = ReactiveMarkdownStream(
                stream_id, update_callback=self._on_stream_update
            )

        # Accumulate the chunk content
        self.accumulated_content += chunk

        # Update the stream with accumulated content
        await self.active_stream.update_async(self.accumulated_content)

    async def _end_stream(self, payload):
        stream_id = payload["stream_id"]

        # Stop spinner if still running
        if self.spinner:
            self.spinner.stop()
            self.spinner = None

        # Final update to markdown stream using our accumulated content
        if self.active_stream and self.current_stream_id == stream_id:
            await self.active_stream.update_async(self.accumulated_content, final=True)
            self.active_stream = None
            self.current_stream_id = None
            self.accumulated_content = ""  # Clear accumulated content

    async def _cancel_stream(self, payload):
        stream_id = payload["stream_id"]

        # Clean up spinner
        if self.spinner:
            self.spinner.stop()
            self.spinner = None

        # Clean up markdown stream
        if self.active_stream and self.current_stream_id == stream_id:
            # Show cancellation message
            self.console.print("[yellow]Stream cancelled[/yellow]")
            self.active_stream = None
            self.current_stream_id = None
            self.accumulated_content = ""  # Clear accumulated content

    async def _show_tool_usage(self, payload):
        """Enhanced tool usage display"""
        tool_name = payload.get("tool_name", "Unknown tool")

        # Finalize current stream
        if self.active_stream:
            await self.active_stream.update_async(self.accumulated_content, final=True)
            self.active_stream = None
            self.accumulated_content = ""

        if self.spinner:
            self.spinner.stop()
            self.spinner = None

        self.console.print()
        self.console.print(
            Rule(f"Executing {tool_name}", align="left", style="secondary")
        )

    async def _hide_tool_usage(self, payload):
        """Clean up after tool execution"""
        # Clear any remaining tool call state
        self.active_tool_calls.clear()
        if self.tool_json_live:
            self.tool_json_live.stop()
            self.tool_json_live = None

    async def _handle_stream_error(self, payload):
        stream_id = payload["stream_id"]
        error = payload["error"]

        # Clean up any active rendering for this stream
        if self.spinner:
            self.spinner.stop()
            self.spinner = None

        if self.active_stream and self.current_stream_id == stream_id:
            self.active_stream = None
            self.current_stream_id = None
            self.accumulated_content = ""  # Clear accumulated content on error

        # Show error message
        self.console.print(f"[red]Stream error: {error}[/red]")

    async def _handle_special_chunks(self, stream_id: str, chunk_data: dict):
        """Handle special chunk types like tool calls"""
        # This would contain your existing logic for detecting
        # tool starts, chain starts, etc. from the chunk_data
        pass

    async def _on_stream_update(self, stream_id: str, line_count: int):
        """Callback for when stream updates"""
        # Optional callback for stream update notifications
        pass

    async def subscriptions(self):
        return [
            MessageType.SHUTDOWN,
            MessageType.TOOL_START,
            MessageType.TOOL_END,
            MessageType.START_STREAM,
            MessageType.STREAM_CHUNK,
            MessageType.END_STREAM,
            MessageType.CANCEL_STREAM,
        ]
