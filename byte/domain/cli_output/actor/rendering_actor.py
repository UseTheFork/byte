import asyncio
from typing import Dict

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
        # Process in smaller chunks to avoid blocking
        lines = self._render_markdown_to_lines(text)

        # Process lines in chunks
        chunk_size = 20
        for i in range(0, len(lines), chunk_size):
            chunk = lines[i : i + chunk_size]
            await self._process_line_chunk(
                chunk, final and i + chunk_size >= len(lines)
            )

            # Yield control frequently
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
        self.active_streams: Dict[str, ReactiveMarkdownStream] = {}
        self.spinners: Dict[str, Live] = {}

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

        # Show initial UI elements
        self.console.print()

        if metadata.stream_type == "agent":
            self.console.print(Rule("Agent", align="left"))

            # Start with spinner
            spinner = Spinner("dots", text="Thinking...")
            live_spinner = Live(
                spinner, console=self.console, transient=True, refresh_per_second=20
            )
            live_spinner.start()
            self.spinners[stream_id] = live_spinner

        # Create markdown stream
        markdown_stream = ReactiveMarkdownStream(
            stream_id, update_callback=self._on_stream_update
        )
        self.active_streams[stream_id] = markdown_stream

    async def _handle_chunk(self, payload):
        stream_id = payload["stream_id"]
        accumulated = payload["accumulated"]
        chunk_data = payload.get("chunk_data", {})

        # Stop spinner if it's running
        if stream_id in self.spinners:
            self.spinners[stream_id].stop()
            del self.spinners[stream_id]

        # Update markdown stream
        if stream_id in self.active_streams:
            await self.active_streams[stream_id].update_async(accumulated)

        # Handle special chunk types (tools, etc.)
        await self._handle_special_chunks(stream_id, chunk_data)

    async def _end_stream(self, payload):
        stream_id = payload["stream_id"]
        final_content = payload["final_content"]

        # Stop spinner if still running
        if stream_id in self.spinners:
            self.spinners[stream_id].stop()
            del self.spinners[stream_id]

        # Final update to markdown stream
        if stream_id in self.active_streams:
            await self.active_streams[stream_id].update_async(final_content, final=True)
            del self.active_streams[stream_id]

    async def _cancel_stream(self, payload):
        stream_id = payload["stream_id"]

        # Clean up spinner
        if stream_id in self.spinners:
            self.spinners[stream_id].stop()
            del self.spinners[stream_id]

        # Clean up markdown stream
        if stream_id in self.active_streams:
            # Show cancellation message
            self.console.print("[yellow]Stream cancelled[/yellow]")
            del self.active_streams[stream_id]

    async def _show_tool_usage(self, payload):
        tool_name = payload.get("tool_name", "Unknown tool")
        self.console.print()
        self.console.print(Rule(f"Using Tool: {tool_name}", align="left"))

    async def _hide_tool_usage(self, payload):
        # Tool finished, no special UI needed
        pass

    async def _handle_stream_error(self, payload):
        stream_id = payload["stream_id"]
        error = payload["error"]

        # Clean up any active rendering for this stream
        if stream_id in self.spinners:
            self.spinners[stream_id].stop()
            del self.spinners[stream_id]

        if stream_id in self.active_streams:
            del self.active_streams[stream_id]

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
            MessageType.START_STREAM,
            MessageType.STREAM_CHUNK,
            MessageType.END_STREAM,
            MessageType.CANCEL_STREAM,
        ]
