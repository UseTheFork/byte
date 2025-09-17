from typing import Any, AsyncGenerator

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from byte.context import make
from byte.core.logging import log
from byte.core.response.formatters import MarkdownStream


class ResponseHandler:
    """Simplified response handler using Rich Live for streaming display."""

    def __init__(self):
        self._accumulated_content = ""

    async def handle_stream(self, event_stream: AsyncGenerator[Any, None]) -> Any:
        """Handle agent response stream with simple Live display."""

        self._accumulated_content = ""
        console = await make("console")
        final_message = None

        async for event in event_stream:
            result = self._process_event(event, console)
            if result:  # If _process_event returns a final message
                final_message = result

        return final_message

    def _process_event(self, event: dict, console: Console) -> Any:
        """Process a single event and update content."""
        event_type = event.get("event", "")
        # event_name = event.get("name", "")

        log.debug(event_type)
        log.debug(event)

        if event_type == "on_chat_model_stream":
            if "chunk" in event["data"]:
                chunk = event["data"]["chunk"]
                text_content = self._extract_text_content(chunk)
                if text_content:
                    self._accumulated_content += text_content
                    self.markdown_stream.update(self._accumulated_content)
        elif event_type == "on_chat_model_start":
            self.markdown_stream = MarkdownStream()
        elif event_type == "on_chat_model_end":
            self.markdown_stream.update(self._accumulated_content, True)
            self._accumulated_content = ""
        elif event_type == "on_tool_start":
            tool_name = event.get("name", "Unknown tool")
            console.print(Panel.fit(Markdown(f"**Using Tool:** {tool_name}")))
        elif event_type == "on_tool_end":
            pass

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
