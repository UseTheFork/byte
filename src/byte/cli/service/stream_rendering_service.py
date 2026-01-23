import re

from langchain_core.messages.ai import AIMessageChunk
from langchain_core.messages.tool import ToolMessage
from rich.live import Live

from byte.cli import MarkdownStream, RuneSpinner
from byte.support import Service
from byte.support.utils import extract_content_from_message, extract_json_from_message


class StreamRenderingService(Service):
    """Service for rendering streaming AI responses with rich formatting and visual feedback.

    Manages the display of streaming content from AI agents, including markdown rendering,
    tool execution visualization, and spinner management. Provides a unified interface
    for handling different message types and streaming modes from LangGraph agents.
    Usage: `await stream_service.handle_message(chunk, "CoderAgent")` -> renders streaming content
    """

    def boot(self) -> None:
        """Initialize the stream rendering service with console and state management.

        Sets up the Rich console, initializes streaming state variables, and prepares
        the markdown stream renderer for handling AI agent responses.
        Usage: Called automatically during service container boot process
        """
        self.console = self.app["console"]

        self.current_stream_id = None
        self.accumulated_content = ""
        self.agent_name = ""
        self.display_mode = "verbose"
        self.spinner = None
        self.stream_started = False
        self.tool_spinner_started = False
        self.active_stream = MarkdownStream(
            console=self.console.console,
            mdargs={"code_theme": self.app["config"].cli.syntax_theme},
        )

    async def _start_tool_message(self):
        """Display tool execution start indicator with visual separation.

        Shows a visual rule separator to indicate transition from AI response
        to tool execution phase, providing clear visual feedback to users.
        Usage: Called automatically when AI response indicates tool usage
        """
        # Tool messages might need different visual treatment
        if self.display_mode in ["verbose", "thinking"]:
            self.console.print()
            self.console.rule("Using Tool")

    async def _update_active_stream(self, final: bool = False):
        """Update the active markdown stream renderer with accumulated content.

        Passes accumulated content to the markdown stream for progressive
        rendering, with optional final flag to indicate stream completion.
        Usage: Called internally during content accumulation and finalization
        """
        if self.active_stream and self.display_mode == "verbose":
            await self.active_stream.update(self.accumulated_content, final=final)

    async def _handle_tool_message(self, message_chunk, metadata):
        pass

    async def _handle_ai_message(self, message_chunk, metadata):
        """Handle AI assistant message chunks with content accumulation and stream management.

        Processes streaming text content from AI responses, manages stream lifecycle
        based on thread IDs, and handles stop conditions for tool usage transitions.
        Usage: Called internally when processing AIMessageChunk instances
        """

        # Start stream on first content (transition from spinner)
        if message_chunk.content and not self.stream_started:
            await self.stop_spinner()
            await self.start_stream_render()
            self.stream_started = True

        # Accumulate and render content
        if message_chunk.content:
            self.accumulated_content += extract_content_from_message(message_chunk)
            if self.display_mode == "verbose":
                await self._update_active_stream()

            if extract_json_from_message(message_chunk) is not None:
                await self.end_stream_render()

        # Handle tool usage - end stream, start tool spinner
        if hasattr(message_chunk, "tool_call_chunks") and message_chunk.tool_call_chunks:
            if not self.tool_spinner_started:
                await self.end_stream_render()
                await self.start_spinner("Using Tool...")
                self.tool_spinner_started = True

        # Check for stream ending conditions
        if hasattr(message_chunk, "response_metadata"):
            if (
                message_chunk.response_metadata.get("stop_reason") == "end_turn"
                or message_chunk.response_metadata.get("stop_reason") == "tool_use"
            ):
                await self.end_stream_render()

    async def _end_tool_message(self, message_chunk, metadata):
        """Handle completion of tool execution with spinner restart.

        Processes tool execution results and restarts the thinking spinner
        to indicate AI is processing the tool output for next response.
        Usage: Called automatically when ToolMessage chunks are received
        """
        await self.stop_spinner()
        await self.start_spinner("Thinking...")
        self.tool_spinner_started = False

    async def _handle_default_message(self, message_chunk, metadata):
        """Handle non-AI, non-Tool message types with basic content processing.

        Provides fallback handling for message types not explicitly supported,
        extracting and accumulating content using basic text extraction methods.
        Usage: Called automatically for unrecognized message chunk types
        """
        # Fallback for other message types - basic content handling
        if message_chunk.content:
            content = extract_content_from_message(message_chunk)
            if content:
                self.accumulated_content += content
                if self.display_mode == "verbose":
                    await self._update_active_stream()

    async def handle_task(self, chunk, agent_name: str):
        self.current_stream_id = f"{chunk.get('name')}:{chunk.get('id')}"
        self.agent_name = agent_name
        is_start = chunk.get("input") is not None

        if chunk.get("name") == "assistant_node":
            if is_start:
                await self.start_spinner("Thinking...")
                self.stream_started = False
                self.tool_spinner_started = False
            else:
                await self.end_stream_render()
                await self.stop_spinner()

    async def handle_message(self, chunk, agent_name: str):
        """Handle streaming message chunks from AI agents with type-specific processing.

        Routes different message types (AI, Tool, etc.) to appropriate handlers for
        proper display formatting and user experience. Manages stream lifecycle
        and content accumulation for smooth rendering.
        Usage: `await service.handle_message((message, metadata), "CoderAgent")` -> processes chunk
        """

        message_chunk, metadata = chunk

        if isinstance(message_chunk, AIMessageChunk):
            await self._handle_ai_message(message_chunk, metadata)
        elif isinstance(message_chunk, ToolMessage):
            await self._end_tool_message(message_chunk, metadata)
        else:
            await self._handle_default_message(message_chunk, metadata)

    async def end_stream_render(self):
        """End the current stream rendering and reset accumulated content."""
        if self.display_mode == "verbose":
            await self._update_active_stream(final=True)
        self.accumulated_content = ""
        self.active_stream = None
        self.current_stream_id = None
        self.console.clear_live()
        await self.stop_spinner()

    def _format_agent_name(self, agent_name: str) -> str:
        """Convert agent class name to readable headline case.

        Usage: "CoderAgent" -> "Coder Agent"
        """
        # Insert space before capital letters (except the first one)
        spaced = re.sub(r"(?<!^)(?=[A-Z])", " ", agent_name)
        return spaced

    async def start_stream_render(self):
        """Initialize a new streaming render session with agent identification.

        Sets up a new markdown stream renderer, displays agent header with
        formatted name, and prepares for content accumulation. Cleans up
        any existing stream before starting the new one.
        Usage: `await service.start_stream_render("thread_123")` -> starts new stream
        """
        if self.active_stream and self.display_mode == "verbose":
            await self._update_active_stream(final=True)

        await self.stop_spinner()

        self.accumulated_content = ""  # Reset accumulated content for new stream
        if self.display_mode == "verbose":
            self.active_stream = MarkdownStream(
                console=self.console.console,
                mdargs={
                    "code_theme": self.app["config"].cli.syntax_theme,
                    "inline_code_lexer": "text",
                },
            )  # Reset the stream renderer

            formatted_name = self._format_agent_name(self.agent_name)
            if self.display_mode in ["verbose"]:
                self.console.rule(f"[primary]{formatted_name}[/primary]", style="primary")

    async def end_stream(self):
        """Complete the streaming session and clean up all rendering state.

        Stops any active spinner, finalizes the current stream render, and
        resets all streaming state for the next interaction cycle.
        Usage: Called automatically at the end of agent execution
        """
        await self.stop_spinner()
        await self.end_stream_render()

    async def stop_spinner(self):
        """Stop the active thinking spinner if one is running.

        Safely stops the Rich Live spinner display, handling cleanup
        and preventing display artifacts during stream transitions.
        Usage: Called automatically during stream lifecycle management
        """
        if self.spinner:
            self.spinner.stop()
            self.spinner = None

    async def start_spinner(self, message="Thinking..."):
        """Start a thinking spinner to indicate AI processing activity.

        Creates and starts a Rich Live spinner with "Thinking..." text to
        provide visual feedback during AI processing or tool execution phases.
        Usage: Called automatically when AI needs to process or think
        """
        if self.display_mode in ["verbose", "thinking"] and not self.spinner:
            # Start with animated spinner
            self.console.set_live()
            spinner = RuneSpinner(text=message, size=15)
            transient = not self.app.running_unit_tests()
            self.spinner = Live(spinner, console=self.console.console, transient=transient, refresh_per_second=20)
            self.spinner.start()

    def set_display_mode(self, mode: str) -> None:
        """Set the display mode for stream rendering.

        Args:
                mode: Display mode - must be "verbose", "thinking", or "silent"

        Raises:
                ValueError: If mode is not one of the valid options

        Usage: `stream_service.set_display_mode("thinking")` -> sets spinner-only mode
        """
        valid_modes = ["verbose", "thinking", "silent"]
        if mode not in valid_modes:
            raise ValueError(f"Invalid display mode '{mode}'. Must be one of: {valid_modes}")
        self.display_mode = mode
