from rich.console import Console
from rich.live import Live
from rich.rule import Rule
from rich.spinner import Spinner

from byte.core.service.base_service import Service
from byte.domain.cli_output.utils.formatters import MarkdownStream


class StreamRenderingService(Service):
    async def boot(self) -> None:
        self.console = await self.make(Console)
        self.console_state = "idle"
        self.accumulated_content = "idle"
        self.active_stream = MarkdownStream()

    async def _start_stream_render(self, payload):
        stream_id = payload["stream_id"]
        metadata = payload["metadata"]

        # Clean up any existing stream
        if self.active_stream:
            await self.active_stream.update("", final=True)

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

        # # Create markdown stream
        # self.active_stream = ReactiveMarkdownStream(
        #     stream_id, update_callback=self._on_stream_update
        # )
