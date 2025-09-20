from typing import Any, AsyncGenerator

from langchain_core.messages import AIMessage
from rich.console import Console
from rich.live import Live
from rich.rule import Rule
from rich.spinner import Spinner

from byte.core.config.mixins import Configurable
from byte.core.response.formatters import MarkdownStream
from byte.core.service.mixins import Bootable, Injectable


class ResponseHandler(Bootable, Configurable, Injectable):
    """Simplified response handler using Rich Live for streaming display."""

    async def boot(self):
        self._accumulated_content = ""

    async def handle_stream(
        self, event_stream: AsyncGenerator[Any, None]
    ) -> AIMessage | None:
        """Handle agent response stream with simple Live display."""

        self._accumulated_content = ""
        self._console = await self.make(Console)

        # Setup a Live Spinner
        spinner = Spinner("dots", text="Thinking...")
        self._live = Live(
            spinner, console=self._console, transient=True, refresh_per_second=20
        )

        final_message = None

        async for event in event_stream:
            result = self._process_event(event)
            if result:  # If _process_event returns a final message
                final_message = result

        return final_message

    def _process_event(self, event: dict) -> AIMessage | None:
        """Process a single event and update content."""
        event_type = event.get("event", "")
        event_name = event.get("name", "")

        # log.debug(event_type)
        # log.debug(event_name)

        if event_type == "on_chat_model_stream":
            if "chunk" in event["data"]:
                chunk = event["data"]["chunk"]
                text_content = self._extract_text_content(chunk)
                if text_content:
                    self._accumulated_content += text_content
                    self.markdown_stream.update(self._accumulated_content)
        elif event_type == "on_chat_model_start":
            self._live.stop()
            self._console.print()
            self._console.print(Rule("Agent", align="left"))
            self.markdown_stream = MarkdownStream()
        elif event_type == "on_chat_model_end":
            self.markdown_stream.update(self._accumulated_content, True)
            self._accumulated_content = ""
        elif event_type == "on_tool_start":
            tool_name = event.get("name", "Unknown tool")
            self._console.print()
            self._console.print(Rule(f"Using Tool: {tool_name}", align="left"))
        elif event_type == "on_tool_end":
            pass
        elif event_type == "on_chain_start":
            if event_name == "LangGraph":
                self._live.start()
            pass
        elif event_type == "on_chain_end":
            if event_name == "LangGraph":
                messages = event["data"]["output"]["messages"]
                last_message = messages[-1] if messages else None
                return last_message
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
