import re

from langchain_core.messages.ai import AIMessageChunk
from langchain_core.messages.tool import ToolMessage
from rich.live import Live

from byte.core.service.base_service import Service
from byte.core.utils import extract_content_from_message
from byte.domain.cli.rich.rune_spinner import RuneSpinner
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.cli.utils.formatters import MarkdownStream


class StreamRenderingService(Service):
    """Service for rendering streaming AI responses with rich formatting and visual feedback.

    Manages the display of streaming content from AI agents, including markdown rendering,
    tool execution visualization, and spinner management. Provides a unified interface
    for handling different message types and streaming modes from LangGraph agents.
    Usage: `await stream_service.handle_message(chunk, "CoderAgent")` -> renders streaming content
    """

    async def boot(self) -> None:
        """Initialize the stream rendering service with console and state management.

        Sets up the Rich console, initializes streaming state variables, and prepares
        the markdown stream renderer for handling AI agent responses.
        Usage: Called automatically during service container boot process
        """
        self.console = await self.make(ConsoleService)

        self.current_stream_id = None
        self.accumulated_content = ""
        self.agent_name = ""
        self.display_mode = "verbose"
        self.spinner = None
        self.active_stream = MarkdownStream(
            console=self.console.console,
            mdargs={"code_theme": self._config.cli.syntax_theme},
        )

    async def handle_message(self, chunk, agent_name: str):
        """Handle streaming message chunks from AI agents with type-specific processing.

        Routes different message types (AI, Tool, etc.) to appropriate handlers for
        proper display formatting and user experience. Manages stream lifecycle
        and content accumulation for smooth rendering.
        Usage: `await service.handle_message((message, metadata), "CoderAgent")` -> processes chunk
        """

        message_chunk, metadata = chunk

        # Set the Agent "class" as the Agent Name
        self.agent_name = agent_name

        # Handle different message types with isinstance checks
        if isinstance(message_chunk, AIMessageChunk):
            # Handle AI assistant responses - normal streaming content
            await self._handle_ai_message(message_chunk, metadata)

        elif isinstance(message_chunk, ToolMessage):
            # Handle tool execution results - might want different formatting
            await self._end_tool_message(message_chunk, metadata)

        else:
            # Handle other message types with default behavior
            await self._handle_default_message(message_chunk, metadata)

    async def _handle_ai_message(self, message_chunk, metadata):
        """Handle AI assistant message chunks with content accumulation and stream management.

        Processes streaming text content from AI responses, manages stream lifecycle
        based on thread IDs, and handles stop conditions for tool usage transitions.
        Usage: Called internally when processing AIMessageChunk instances
        """

        # Check if we need to start a new stream
        if metadata.get("thread_id") and metadata["thread_id"] != self.current_stream_id:
            await self.start_stream_render(metadata["thread_id"])

        # Append message content to accumulated content
        if message_chunk.content:
            self.accumulated_content += extract_content_from_message(message_chunk)
            if self.display_mode == "verbose":
                await self._update_active_stream()

        if hasattr(message_chunk, "response_metadata"):
            # Check for stream ending conditions
            if (
                message_chunk.response_metadata.get("stop_reason") == "end_turn"
                or message_chunk.response_metadata.get("stop_reason") == "tool_use"
            ):
                await self.end_stream_render()

                if message_chunk.response_metadata.get("stop_reason") == "tool_use":
                    await self._start_tool_message()

    async def _start_tool_message(self):
        """Display tool execution start indicator with visual separation.

        Shows a visual rule separator to indicate transition from AI response
        to tool execution phase, providing clear visual feedback to users.
        Usage: Called automatically when AI response indicates tool usage
        """
        # Tool messages might need different visual treatment

        self.console.print()
        self.console.rule("Using Tool")

        # We reset the stream_id here to make it look like a new stream
        self.current_stream_id = ""

    async def _end_tool_message(self, message_chunk, metadata):
        """Handle completion of tool execution with spinner restart.

        Processes tool execution results and restarts the thinking spinner
        to indicate AI is processing the tool output for next response.
        Usage: Called automatically when ToolMessage chunks are received
        """
        # PLaceholder for maybe displaying the result of the tool message?
        self.console.print()
        # Restart the spinner since usually the AI will think after this.
        await self.start_spinner()

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

    async def handle_update(self, chunk):
        """Handle state update chunks from LangGraph execution with node transition management.

        Processes graph node transitions, managing stream lifecycle when moving
        between assistant and tool nodes. Handles stream pausing and resumption
        for smooth visual transitions during complex agent workflows.
        Usage: Called automatically when processing graph state updates
        """

        if isinstance(chunk, dict):
            for key in chunk.keys():
                # If we see a 'tools' key, we're transitioning to tool execution
                if key == "tools":
                    # End the current stream since tools don't stream content
                    await self.end_stream_render()
                    # Store the previous stream ID so we can resume later
                    self._previous_stream_id = self.current_stream_id

                # If we're transitioning back to assistant after tools
                elif key == "assistant" and hasattr(self, "_previous_stream_id"):
                    # Resume streaming with the previous stream ID
                    await self.start_stream_render(self._previous_stream_id)
                    # Clear the stored previous ID
                    delattr(self, "_previous_stream_id")

                # For any other new node transition
                elif key != self.current_stream_id:
                    await self.end_stream_render()

    async def end_stream_render(self):
        """End the current stream rendering and reset accumulated content."""
        if self.display_mode == "verbose":
            await self._update_active_stream(final=True)
        self.accumulated_content = ""
        self.active_stream = None
        self.current_stream_id = None
        await self.stop_spinner()

    async def start_stream_render(self, stream_id):
        """Initialize a new streaming render session with agent identification.

        Sets up a new markdown stream renderer, displays agent header with
        formatted name, and prepares for content accumulation. Cleans up
        any existing stream before starting the new one.
        Usage: `await service.start_stream_render("thread_123")` -> starts new stream
        """
        if self.active_stream and self.display_mode == "verbose":
            await self._update_active_stream(final=True)

        await self.stop_spinner()

        self.current_stream_id = stream_id
        self.accumulated_content = ""  # Reset accumulated content for new stream
        if self.display_mode == "verbose":
            self.active_stream = MarkdownStream(
                console=self.console.console,
                mdargs={
                    "code_theme": self._config.cli.syntax_theme,
                    "inline_code_lexer": "text",
                },
            )  # Reset the stream renderer

            formatted_name = self._format_agent_name(self.agent_name)
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

    async def start_spinner(self):
        """Start a thinking spinner to indicate AI processing activity.

        Creates and starts a Rich Live spinner with "Thinking..." text to
        provide visual feedback during AI processing or tool execution phases.
        Usage: Called automatically when AI needs to process or think
        """
        if self.display_mode in ["verbose", "thinking"]:
            # Start with animated spinner
            spinner = RuneSpinner(text="Thinking...", size=15)
            self.spinner = Live(spinner, console=self.console.console, transient=True, refresh_per_second=20)
            self.spinner.start()

    async def _update_active_stream(self, final: bool = False):
        """Update the active markdown stream renderer with accumulated content.

        Passes accumulated content to the markdown stream for progressive
        rendering, with optional final flag to indicate stream completion.
        Usage: Called internally during content accumulation and finalization
        """
        if self.active_stream and self.display_mode == "verbose":
            await self.active_stream.update(self.accumulated_content, final=final)

    def _format_agent_name(self, agent_name: str) -> str:
        """Convert agent class name to readable headline case.

        Usage: "CoderAgent" -> "Coder Agent"
        """
        # Insert space before capital letters (except the first one)
        spaced = re.sub(r"(?<!^)(?=[A-Z])", " ", agent_name)
        return spaced

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
