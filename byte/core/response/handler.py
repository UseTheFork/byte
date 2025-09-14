from typing import TYPE_CHECKING, Any, AsyncGenerator, Dict

from rich.live import Live
from rich.spinner import Spinner

from .formatters import (
    ErrorFormatter,
    ResponseFormatter,
    TextChunkFormatter,
    ThinkingFormatter,
    ToolCallFormatter,
    ToolResultFormatter,
)
from .types import ResponseChunk, ResponseOptions, ResponseType

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

    async def handle_stream(
        self,
        stream: AsyncGenerator[Any, None],
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

        text_formatter = None

        # Show loading spinner while waiting for first response
        spinner = Spinner("dots", text="Thinking...")
        loading_display = Live(spinner, console=console, refresh_per_second=10)
        loading_display.start()
        first_chunk_received = False

        try:
            async for raw_chunk in stream:
                # Stop loading spinner on first chunk
                if not first_chunk_received:
                    loading_display.stop()
                    first_chunk_received = True

                chunk = self._normalize_chunk(raw_chunk)
                # Get or create formatter instance for this stream
                if chunk.type not in self._active_formatters:
                    formatter_class = self._formatter_classes.get(chunk.type)
                    if formatter_class:
                        self._active_formatters[chunk.type] = formatter_class()

                formatter = self._active_formatters.get(chunk.type)

                # Track text formatter for finalization
                if chunk.type == ResponseType.TEXT_CHUNK:
                    text_formatter = formatter

                if formatter:
                    await formatter.format_and_display(chunk, console, options)

        finally:
            # Ensure loading spinner is stopped
            if "loading_display" in locals() and not first_chunk_received:
                loading_display.stop()

            # Finalize text formatter to make content scrollable
            if text_formatter and hasattr(text_formatter, "finalize"):
                text_formatter.finalize(console)  # pyright: ignore[reportAttributeAccessIssue]

            # Clear active formatters for next stream
            self._active_formatters.clear()

    def _normalize_chunk(self, raw_chunk: Any) -> ResponseChunk:
        """Convert raw agent output to normalized ResponseChunk.

        Handles different chunk formats from various LangChain/LangGraph agents
        and converts them to a consistent internal representation.
        """
        # Handle tuple format (message, metadata) from LangGraph stream_mode="messages"
        if isinstance(raw_chunk, tuple) and len(raw_chunk) >= 1:
            message = raw_chunk[0]
            metadata = raw_chunk[1] if len(raw_chunk) > 1 else None

            # Extract content from AIMessageChunk (should have content since we filter upstream)
            if hasattr(message, "content"):
                return ResponseChunk(
                    type=ResponseType.TEXT_CHUNK,
                    content=message.content or "",
                    metadata=metadata,
                    raw_chunk=raw_chunk,
                )

            # Handle tool calls
            if hasattr(message, "tool_calls") and message.tool_calls:
                tool_call = message.tool_calls[0]  # Handle first tool call
                return ResponseChunk(
                    type=ResponseType.TOOL_CALL,
                    content="",
                    metadata={
                        "tool_name": tool_call.get("name", "unknown"),
                        "parameters": tool_call.get("args", {}),
                    },
                    raw_chunk=raw_chunk,
                )

        # Handle direct message chunks
        elif hasattr(raw_chunk, "content"):
            return ResponseChunk(
                type=ResponseType.TEXT_CHUNK,
                content=raw_chunk.content or "",
                raw_chunk=raw_chunk,
            )

        # Handle tool results or other types
        elif hasattr(raw_chunk, "type"):
            chunk_type = self._map_chunk_type(raw_chunk.type)
            return ResponseChunk(
                type=chunk_type,
                content=str(raw_chunk.content) if hasattr(raw_chunk, "content") else "",
                raw_chunk=raw_chunk,
            )

        # This should rarely be reached now that we filter upstream
        return ResponseChunk(
            type=ResponseType.TEXT_CHUNK,
            content="",
            raw_chunk=raw_chunk,
        )

    def _map_chunk_type(self, raw_type: str) -> ResponseType:
        """Map raw chunk types to ResponseType enum."""
        type_mapping = {
            "tool_call": ResponseType.TOOL_CALL,
            "tool_result": ResponseType.TOOL_RESULT,
            "thinking": ResponseType.THINKING,
            "error": ResponseType.ERROR,
        }
        return type_mapping.get(raw_type, ResponseType.TEXT_CHUNK)

    def register_formatter(
        self, response_type: ResponseType, formatter_class: type
    ) -> None:
        """Register a custom formatter class for a specific response type.

        Usage: `handler.register_formatter(ResponseType.CUSTOM, CustomFormatter)`
        """
        self._formatter_classes[response_type] = formatter_class
