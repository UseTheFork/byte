from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from rich.live import Live
from rich.markdown import Markdown

from .types import ResponseChunk, ResponseOptions

if TYPE_CHECKING:
    from rich.console import Console


class ResponseFormatter(ABC):
    """Base formatter for different types of agent responses."""

    @abstractmethod
    async def format_and_display(
        self, chunk: ResponseChunk, console: "Console", options: ResponseOptions
    ) -> None:
        """Format and display a response chunk to the console."""
        pass


class TextChunkFormatter(ResponseFormatter):
    """Formatter for regular text content chunks with markdown support."""

    def __init__(self):
        self._accumulated_content = ""
        self._live_display: Optional[Live] = None

    async def format_and_display(
        self, chunk: ResponseChunk, console: "Console", options: ResponseOptions
    ) -> None:
        """Stream markdown content with live rendering."""
        if not chunk.content:
            return

        # Accumulate content
        self._accumulated_content += chunk.content

        # Create live display on first chunk
        if self._live_display is None:
            self._live_display = Live(
                console=console,
                refresh_per_second=10,  # Smooth but not excessive
                auto_refresh=True,
            )
            self._live_display.start()

        # Render accumulated markdown
        try:
            markdown = Markdown(self._accumulated_content)
            self._live_display.update(markdown)
        except Exception:
            # Fallback to plain text if markdown parsing fails
            self._live_display.update(self._accumulated_content)

    def finalize(self, console: "Console") -> None:
        """Finalize the display when streaming is complete."""
        if self._live_display:
            self._live_display.stop()
            # Print final markdown to make it scrollable
            if self._accumulated_content:
                console.print(Markdown(self._accumulated_content))
            self._reset()

    def _reset(self) -> None:
        """Reset formatter state for next use."""
        self._accumulated_content = ""
        self._live_display = None


class ToolCallFormatter(ResponseFormatter):
    """Formatter for tool call invocations."""

    async def format_and_display(
        self, chunk: ResponseChunk, console: "Console", options: ResponseOptions
    ) -> None:
        """Display tool call with parameters if enabled."""
        if not options.show_tool_calls:
            return

        tool_name = (
            chunk.metadata.get("tool_name", "unknown") if chunk.metadata else "unknown"
        )
        console.print(f"\n[info]Calling tool:[/info] [bold]{tool_name}[/bold]")

        if options.verbose and chunk.metadata and "parameters" in chunk.metadata:
            console.print(f"   Parameters: {chunk.metadata['parameters']}")


class ToolResultFormatter(ResponseFormatter):
    """Formatter for tool execution results."""

    async def format_and_display(
        self, chunk: ResponseChunk, console: "Console", options: ResponseOptions
    ) -> None:
        """Display tool results if enabled."""
        if not options.show_tool_results:
            return

        tool_name = (
            chunk.metadata.get("tool_name", "unknown") if chunk.metadata else "unknown"
        )
        console.print(f"[success]Tool completed:[/success] [bold]{tool_name}[/bold]")

        if options.verbose and chunk.content:
            console.print(
                f"   Result: {chunk.content[:100]}{'...' if len(chunk.content) > 100 else ''}"
            )


class ThinkingFormatter(ResponseFormatter):
    """Formatter for agent reasoning/thinking steps."""

    async def format_and_display(
        self, chunk: ResponseChunk, console: "Console", options: ResponseOptions
    ) -> None:
        """Display thinking steps if enabled."""
        if not options.show_thinking:
            return

        console.print(f"[dim]{chunk.content}[/dim]")


class ErrorFormatter(ResponseFormatter):
    """Formatter for error responses."""

    async def format_and_display(
        self, chunk: ResponseChunk, console: "Console", options: ResponseOptions
    ) -> None:
        """Display errors with appropriate styling."""
        console.print(f"[error]Error:[/error] {chunk.content}")
