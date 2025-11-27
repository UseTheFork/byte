import asyncio
from abc import ABC, abstractmethod
from typing import Any, Literal, Optional

from langgraph.graph.state import CompiledStateGraph, RunnableConfig

from byte.core.event_bus import EventType, Payload
from byte.core.logging import log
from byte.core.mixins.bootable import Bootable
from byte.core.mixins.configurable import Configurable
from byte.core.mixins.eventable import Eventable
from byte.core.mixins.injectable import Injectable
from byte.domain.agent.schemas import AssistantContextSchema
from byte.domain.agent.state import BaseState
from byte.domain.cli.service.stream_rendering_service import (
    StreamRenderingService,
)
from byte.domain.memory.service.memory_service import MemoryService


class Agent(ABC, Bootable, Configurable, Injectable, Eventable):
    """Base class for all agent services providing common graph management functionality.

    Defines the interface for agent services with lazy-loaded graph compilation,
    tool management, and memory integration. Subclasses must implement the build
    method to define their specific agent behavior and routing logic.
    Usage: `class MyAgent(BaseAgent): async def build(self): ...`
    """

    _graph: Optional[CompiledStateGraph] = None

    @abstractmethod
    async def build(self) -> CompiledStateGraph:
        """Build and compile the agent graph with memory and tools.

        Must be implemented by subclasses to define their specific agent
        behavior, routing logic, and tool integration patterns.
        Usage: Override in subclass to create domain-specific agent graphs
        """
        pass

    async def _handle_stream_event(self, mode: str, chunk: Any):
        """Handle individual stream events for display and final message extraction.

        Args:
                mode: The stream mode ("values", "updates", "messages", or "custom")
                chunk: The data chunk from that stream mode
        """
        stream_rendering_service = await self.make(StreamRenderingService)

        # Filter and process based on mode
        if mode == "messages":
            # Handle LLM token streaming
            await stream_rendering_service.handle_message(chunk, self.__class__.__name__)

        elif mode == "updates":
            # Handle state updates after each step
            # await stream_rendering_service.handle_update(chunk)
            pass
        elif mode == "values":
            # Handle full state after each step - could be used for progress tracking
            pass
        elif mode == "custom":
            # Handle custom data from get_stream_writer()
            pass

        return chunk

    async def execute(
        self,
        request: str,
        thread_id: Optional[str] = None,
        display_mode: Literal["verbose", "thinking", "silent"] = "verbose",
    ):
        """Stream agent responses using astream_events for comprehensive event handling.

        Yields events from the agent graph processing, enabling fine-grained
        control over streaming display and tool execution visualization.

        Args:
                request: The request data to process
                thread_id: Optional thread ID for conversation context
                display_mode: Display mode - "verbose", "thinking", or "silent" (default: "verbose")

        Usage: `async for event in agent.stream(request): ...`
        """
        # Get or create thread ID
        if thread_id is None:
            memory_service = await self.make(MemoryService)
            thread_id = await memory_service.get_or_create_thread()

        # Create configuration with thread ID
        config = RunnableConfig(configurable={"thread_id": thread_id})

        # Create initial state using the agent's state class
        initial_state = BaseState({"user_request": request})

        # Get the graph and stream events
        graph = await self.get_graph()

        stream_rendering_service = await self.make(StreamRenderingService)
        stream_rendering_service.set_display_mode(display_mode)

        await stream_rendering_service.start_spinner()

        # Create a task so we can cancel it properly
        stream_task = asyncio.create_task(self._run_stream(graph, initial_state, config, stream_rendering_service))

        try:
            processed_event = await stream_task
        except (KeyboardInterrupt, asyncio.CancelledError):
            # Cancel the stream task properly
            stream_task.cancel()
            try:
                await stream_task
            except asyncio.CancelledError:
                pass
            log.info("Agent execution cancelled by user")
            return None
        finally:
            await stream_rendering_service.end_stream()

        # Create payload with event type
        payload = Payload(
            event_type=EventType.POST_AGENT_EXECUTION,
            data={"processed_event": processed_event},
        )

        await self.emit(payload)

        return processed_event

    async def _run_stream(
        self,
        graph: CompiledStateGraph,
        initial_state: BaseState,
        config: RunnableConfig,
        stream_rendering_service: StreamRenderingService,
    ):
        """Helper method to run the stream in a cancellable task.

        Args:
                graph: The compiled state graph to execute
                initial_state: The initial state for the graph
                config: The runnable configuration with thread ID
                stream_rendering_service: Service for rendering stream output

        Returns:
                The final processed event from the stream

        Usage: Called internally by execute() to run the stream in a cancellable task
        """
        processed_event = None
        async for mode, chunk in graph.astream(
            input=initial_state,
            config=config,
            stream_mode=["values", "updates", "messages", "custom"],
            context=await self.get_assistant_runnable(),
        ):
            processed_event = await self._handle_stream_event(mode, chunk)
        return processed_event

    async def get_checkpointer(self):
        # Get memory for persistence
        memory_service = await self.make(MemoryService)
        checkpointer = await memory_service.get_saver()
        return checkpointer

    def get_tools(self):
        return []

    async def get_graph(self) -> CompiledStateGraph:
        """Get or create the agent graph with current tools.

        Lazy-loads the graph with all registered tools and memory integration.
        The graph is cached until tools are modified to avoid rebuilding.
        Usage: `graph = await agent_service.get_graph()` -> ready for agent tasks
        """
        if self._graph is None:
            self._graph = await self.build()
        return self._graph

    @abstractmethod
    async def get_assistant_runnable(self) -> AssistantContextSchema:
        """Get the assistant runnable for this agent.

        Must be implemented by subclasses to return their specific assistant
        implementation, which defines the core LLM interaction pattern.
        Usage: Override in subclass to provide domain-specific assistant logic
        """
        pass
