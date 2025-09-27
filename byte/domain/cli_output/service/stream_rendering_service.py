from rich.console import Console
from rich.rule import Rule

from byte.core.service.base_service import Service
from byte.domain.cli_output.utils.formatters import MarkdownStream


class StreamRenderingService(Service):
    async def boot(self) -> None:
        self.console = await self.make(Console)
        self.console_state = "idle"

        self.current_stream_id = ""
        self.accumulated_content = ""
        self.spinner = None
        self.active_stream = MarkdownStream()

    async def handle_message(self, chunk):
        message_chunk, metadata = chunk

        # Check if we need to start a new stream
        if (
            metadata.get("langgraph_node")
            and metadata["langgraph_node"] != self.current_stream_id
        ):
            await self.start_stream_render(metadata["langgraph_node"])

        # Append message content to accumulated content
        if message_chunk.content:
            self.accumulated_content += message_chunk.content
            await self._update_active_stream()

    async def handle_update(self, chunk):
        # Check if we have a new stream key that differs from current_stream_id
        if isinstance(chunk, dict):
            for key in chunk.keys():
                if key != self.current_stream_id:
                    await self.end_stream_render()
                    break

    async def end_stream_render(self):
        """End the current stream rendering and reset accumulated content."""
        await self._update_active_stream(final=True)
        self.accumulated_content = ""

    async def start_stream_render(self, stream_id):
        # Clean up any existing stream
        if self.active_stream:
            await self._update_active_stream(final=True)

        # if self.spinner:
        #     self.spinner.stop()

        self.current_stream_id = stream_id
        self.accumulated_content = ""  # Reset accumulated content for new stream

        self.console.print(Rule("Agent", align="left"))

        # Disable spinner for now
        # Start with spinner
        # spinner = Spinner("dots", text="Thinking...")
        # self.spinner = Live(
        #     spinner, console=self.console, transient=True, refresh_per_second=20
        # )
        # self.spinner.start()

        # # Create markdown stream
        # self.active_stream = ReactiveMarkdownStream(
        #     stream_id, update_callback=self._on_stream_update
        # )

    async def _update_active_stream(self, final: bool = False):
        """Update the active stream with accumulated content."""
        if self.active_stream:
            await self.active_stream.update(self.accumulated_content, final=final)
