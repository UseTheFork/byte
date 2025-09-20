import asyncio
from typing import Dict

from rich.console import Console
from rich.live import Live
from rich.rule import Rule
from rich.spinner import Spinner
from rich.text import Text

from byte.core.actors.base import Actor
from byte.core.actors.message import Message, MessageBus, MessageType
from byte.core.response.formatters import MarkdownStream
from byte.core.ui.prompt import PromptHandler


class InputActor(Actor):
    def __init__(self, name: str, message_bus, container):
        super().__init__(name, message_bus, container)
        self.prompt_handler = None
        self.input_task = None

    async def on_start(self):
        """Initialize prompt handler and start input loop"""
        self.prompt_handler = PromptHandler()
        await self.prompt_handler.initialize()

        # Start input gathering in background
        self.input_task = asyncio.create_task(self._input_loop())

    async def on_stop(self):
        """Clean up input handling"""
        if self.input_task and not self.input_task.done():
            self.input_task.cancel()
            try:
                await self.input_task
            except asyncio.CancelledError:
                pass

    async def handle_message(self, message: Message):
        # Input actor primarily sends messages, doesn't handle many
        if message.type == MessageType.SHUTDOWN:
            await self.stop()

    async def _input_loop(self):
        """Main input gathering loop"""
        while self.running:
            try:
                # Get user input (this will block until input is received)
                user_input = await self.prompt_handler.get_input_async("> ")

                if user_input.strip():
                    # Determine if this is a command or regular input
                    if user_input.startswith("/"):
                        await self.send_to(
                            "command",
                            Message(
                                type=MessageType.COMMAND_INPUT,
                                payload={"input": user_input},
                            ),
                        )
                    else:
                        await self.send_to(
                            "agent",
                            Message(
                                type=MessageType.USER_INPUT,
                                payload={"input": user_input},
                            ),
                        )

            except KeyboardInterrupt:
                # User wants to exit
                await self.broadcast(
                    Message(
                        type=MessageType.SHUTDOWN, payload={"reason": "user_interrupt"}
                    )
                )
                break
            except Exception as e:
                await self.on_error(e)


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

        # Your existing line processing logic here
        # but broken into smaller, non-blocking pieces

        if is_final and self.live:
            self.live.update(Text(""))
            self.live.stop()
            self.live = None


class RenderingActor(Actor):
    def __init__(self, name: str, message_bus, container=None):
        super().__init__(name, message_bus, container)
        self.console = Console()
        self.active_streams: Dict[str, ReactiveMarkdownStream] = {}
        self.spinners: Dict[str, Live] = {}

    async def handle_message(self, message: Message):
        if message.type == MessageType.START_STREAM:
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

    async def setup_subscriptions(self, message_bus: MessageBus):
        message_bus.subscribe(self.name, MessageType.START_STREAM)
        message_bus.subscribe(self.name, MessageType.STREAM_CHUNK)
        message_bus.subscribe(self.name, MessageType.END_STREAM)
        message_bus.subscribe(self.name, MessageType.CANCEL_STREAM)
