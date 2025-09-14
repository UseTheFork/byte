from typing import TYPE_CHECKING, Any, AsyncGenerator, Optional, Set

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

from .types import ResponseOptions

if TYPE_CHECKING:
    pass


class ResponseHandler:
    """Simplified response handler using Rich Live for streaming display."""

    def __init__(self):
        self._accumulated_content = ""
        self._processed_events: Set[str] = set()
        self._live: Optional[Live] = None
        # Compatibility property for interaction service
        self._active_live = None

    async def handle_stream(
        self,
        event_stream: AsyncGenerator[Any, None],
        console: Console,
        options: ResponseOptions = None,
    ) -> None:
        """Handle agent response stream with simple Live display."""
        if options is None:
            options = ResponseOptions()

        self._accumulated_content = ""
        self._processed_events.clear()

        # Start Live display
        self._live = Live(console=console, refresh_per_second=20)
        self._live.start()
        # Set compatibility reference for interaction service
        self._active_live = self._live

        try:
            async for event in event_stream:
                self._process_event(event, options)
        finally:
            # Stop live display and print final content
            if self._live:
                self._live.stop()
                # if self._accumulated_content.strip():
                #     console.print(Markdown(self._accumulated_content))
            self._live = None
            self._active_live = None

    def _process_event(self, event: dict, options: ResponseOptions):
        """Process a single event and update content."""
        event_type = event.get("event", "")

        # Only deduplicate non-streaming events
        if event_type != "on_chat_model_stream":
            event_id = f"{event.get('run_id', '')}-{event_type}-{event.get('name', '')}"
            if event_id in self._processed_events:
                return
            self._processed_events.add(event_id)

        content_added = False

        if event_type == "on_chat_model_stream":
            if "chunk" in event["data"]:
                chunk = event["data"]["chunk"]
                text_content = self._extract_text_content(chunk)
                if text_content:
                    self._accumulated_content += text_content
                    content_added = True

        elif event_type == "on_tool_start" and options.show_tool_calls:
            tool_name = event.get("name", "Unknown tool")
            self._accumulated_content += f"\n\n**Using Tool:** {tool_name}\n\n"
            content_added = True

        elif event_type == "on_tool_end" and options.show_tool_results:
            tool_name = event.get("name", "Unknown tool")
            self._accumulated_content += f"\n\n✅ **Tool completed:** {tool_name}\n\n"
            content_added = True

        # Update live display if content was added
        if content_added and self._live:
            self._live.update(Markdown(self._accumulated_content))

    def _extract_text_content(self, chunk) -> str:
        """Extract text content from LLM chunk."""
        if hasattr(chunk, "content"):
            if isinstance(chunk.content, str):
                return chunk.content
            elif isinstance(chunk.content, list) and chunk.content:
                text_parts = []
                for item in chunk.content:
                    if isinstance(item, dict):
                        if item.get("type") == "text" and "text" in item:
                            text_parts.append(item["text"])
                        elif "text" in item and item.get("type") != "input_json_delta":
                            text_parts.append(item["text"])
                    elif isinstance(item, str):
                        text_parts.append(item)
                return "".join(text_parts)
        return ""
