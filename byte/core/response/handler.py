from typing import TYPE_CHECKING, Any, AsyncGenerator, Dict

from rich.live import Live
from rich.markdown import Markdown

from .formatters import (
    ErrorFormatter,
    ResponseFormatter,
    TextChunkFormatter,
    ThinkingFormatter,
    ToolCallFormatter,
    ToolResultFormatter,
)
from .types import ResponseOptions, ResponseType

if TYPE_CHECKING:
    from rich.console import Console


class ResponseHandler:
    """Centralized service for handling different types of agent responses.

    Provides unified processing of agent outputs including text chunks, tool calls,
    tool results, and metadata with appropriate console formatting and display options.
    Usage: `await response_handler.handle_stream(agent_stream, console, options)`
    """

    def __init__(self):
        self._formatter_classes: Dict[ResponseType, type] = {
            ResponseType.TEXT_CHUNK: TextChunkFormatter,
            ResponseType.TOOL_CALL: ToolCallFormatter,
            ResponseType.TOOL_RESULT: ToolResultFormatter,
            ResponseType.THINKING: ThinkingFormatter,
            ResponseType.ERROR: ErrorFormatter,
        }
        self._active_formatters: Dict[ResponseType, ResponseFormatter] = {}
        self._accumulated_content = ""

    async def handle_stream(
        self,
        event: AsyncGenerator[Any, None],
        console: "Console",
        options: ResponseOptions = None,
    ) -> None:
        """Handle agent response stream with type-aware formatting.

        Processes each chunk in the stream, identifies its type, and delegates
        to the appropriate formatter for console display.
        Usage: `await handler.handle_stream(coder_service.stream_code(args), console)`
        """
        if options is None:
            options = ResponseOptions()

        self._accumulated_content = ""  # Reset for new stream
        with Live(
            renderable=Markdown(""), console=console, refresh_per_second=20
        ) as live:
            # Store reference to active live display for interaction tools
            self._active_live = live
            try:
                async for stream_event in event:
                    self.process_event(stream_event, live)
            finally:
                # Clear reference when done
                self._active_live = None

    def process_event(self, event, live: Live):
        output = ""

        if event["event"] == "on_chat_model_start":
            output = "\nThinking...\n"
        elif event["event"] == "on_chat_model_stream":
            if "chunk" in event["data"]:
                chunk = event["data"]["chunk"]
                if hasattr(chunk, "content"):
                    if isinstance(chunk.content, str):
                        # Direct string content
                        output = chunk.content
                    elif isinstance(chunk.content, list) and chunk.content:
                        # List of content items - extract text from appropriate types
                        text_parts = []
                        for item in chunk.content:
                            if isinstance(item, dict):
                                # Handle different content types
                                if item.get("type") == "text" and "text" in item:
                                    text_parts.append(item["text"])
                                elif (
                                    "text" in item
                                    and item.get("type") != "input_json_delta"
                                ):
                                    # Include text content that's not JSON delta
                                    text_parts.append(item["text"])
                            elif isinstance(item, str):
                                text_parts.append(item)
                        output = "".join(text_parts)
        elif event["event"] == "on_tool_start":
            tool_name = event.get("name", "Unknown tool")
            output = f"\nUsing Tool: {tool_name}"
        elif event["event"] == "on_tool_end":
            output = "\n✅ Tool Use Complete"
        elif event["event"] == "on_chain_end" and event["name"] == "LangGraph":
            final_message = event["data"]["output"]["messages"][-1]
            if hasattr(final_message, "content"):
                if isinstance(final_message.content, str):
                    # Anthropic format
                    output = final_message.content
                elif isinstance(final_message.content, list) and final_message.content:
                    # OpenAI format
                    output = final_message.content[0].get("text", "")
                live.update(Markdown(output))
                return

        if output:
            self._accumulated_content += output
            live.update(Markdown(self._accumulated_content))
