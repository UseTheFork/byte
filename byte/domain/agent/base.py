from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Annotated, Any, Optional, Type, TypedDict

from langgraph.graph.message import AnyMessage, add_messages
from langgraph.graph.state import CompiledStateGraph, Runnable, RunnableConfig

from byte.core.config.mixins import Configurable
from byte.core.service.mixins import Bootable, Injectable
from byte.domain.cli_output.service.stream_rendering_service import (
    StreamRenderingService,
)
from byte.domain.memory.service import MemoryService

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph


class BaseState(TypedDict):
    """Base state that all agents inherit."""

    messages: Annotated[list[AnyMessage], add_messages]
    file_context: str


class BaseAssistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    async def __call__(self, state: BaseState, config: RunnableConfig):
        while True:
            result = self.runnable.invoke(state)
            # If the LLM happens to return an empty response, we will re-prompt it
            # for an actual response.
            if not result.tool_calls and (
                not result.content
                or (
                    isinstance(result.content, list)
                    and not result.content[0].get("text")
                )
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}


class Agent(ABC, Bootable, Configurable, Injectable):
    """Base class for all agent services providing common graph management functionality.

    Defines the interface for agent services with lazy-loaded graph compilation,
    tool management, and memory integration. Subclasses must implement the build
    method to define their specific agent behavior and routing logic.
    Usage: `class MyAgent(BaseAgent): async def build(self): ...`
    """

    name: str = ""
    _graph: Optional[CompiledStateGraph] = None

    @abstractmethod
    async def build(self) -> "CompiledStateGraph":
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
            message_chunk, metadata = chunk
            if message_chunk.content:
                await stream_rendering_service.handle_message(chunk)
        elif mode == "updates":
            # Handle state updates after each step
            # chunk will be like {'node_name': {'key': 'value'}}
            await stream_rendering_service.handle_update(chunk)
        elif mode == "values":
            # Handle full state after each step
            # log.info(f"-----------------{mode}------------------")
            # log.info(chunk)
            pass
        elif mode == "custom":
            # Handle custom data from get_stream_writer()
            # log.info(f"-----------------{mode}------------------")
            # log.info(chunk)
            pass

        return chunk

    async def execute(
        self,
        request: Any,
        thread_id: Optional[str] = None,
    ):
        """Stream agent responses using astream_events for comprehensive event handling.

        Yields events from the agent graph processing, enabling fine-grained
        control over streaming display and tool execution visualization.
        Usage: `async for event in agent.stream(request): ...`
        """
        # Get or create thread ID
        if thread_id is None:
            memory_service = await self.make(MemoryService)
            thread_id = memory_service.create_thread()

        # Create configuration with thread ID
        config = RunnableConfig(configurable={"thread_id": thread_id})

        # Create initial state using the agent's state class
        State = self.get_state_class()
        initial_state = State(**request)

        # Get the graph and stream events
        graph = await self.get_graph()

        async for mode, chunk in graph.astream(
            input=initial_state,
            config=config,
            stream_mode=["values", "updates", "messages", "custom"],
        ):
            processed_event = await self._handle_stream_event(mode, chunk)

        return processed_event

    def get_state_class(self) -> Type[TypedDict]:  # pyright: ignore[reportInvalidTypeForm]
        """Return the state class for this agent.

        Override in subclasses to customize state structure.
        Usage: `StateClass = self.get_state_class()` -> agent-specific state
        """
        return BaseState

    def get_tools(self):
        return []

    async def get_graph(self) -> "CompiledStateGraph":
        """Get or create the agent graph with current tools.

        Lazy-loads the graph with all registered tools and memory integration.
        The graph is cached until tools are modified to avoid rebuilding.
        Usage: `graph = await agent_service.get_graph()` -> ready for agent tasks
        """
        if self._graph is None:
            self._graph = await self.build()
        return self._graph
