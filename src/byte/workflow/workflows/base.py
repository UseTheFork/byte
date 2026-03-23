from abc import ABC, abstractmethod
from typing import Optional

from langgraph.graph.state import CompiledStateGraph, RunnableConfig

from byte.agent import BaseState
from byte.memory import MemoryService
from byte.support.mixins import Bootable, Configurable, Eventable


class BaseWorkflow(ABC, Bootable, Eventable, Configurable):
    """ """

    _graph: Optional[CompiledStateGraph] = None

    @abstractmethod
    async def build(self) -> CompiledStateGraph:
        """Build and compile the agent graph with memory and tools.

        Must be implemented by subclasses to define their specific agent
        behavior, routing logic, and tool integration patterns.
        Usage: Override in subclass to create domain-specific agent graphs
        """
        pass

    async def compile(self, request: str, thread_id: Optional[str] = None):
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
            memory_service = self.app.make(MemoryService)
            thread_id = await memory_service.get_or_create_thread()

        # Create configuration with thread ID
        config = RunnableConfig(configurable={"thread_id": thread_id})

        # Create initial state using the agent's state class
        initial_state = BaseState({"user_request": request})

        # Get the graph and stream events
        graph = await self.get_graph()

        return graph, initial_state, config

    async def get_checkpointer(self):
        # Get memory for persistence
        memory_service = self.app.make(MemoryService)
        checkpointer = await memory_service.get_saver()
        return checkpointer

    async def get_graph(self) -> CompiledStateGraph:
        """Get or create the agent graph with current tools.

        Lazy-loads the graph with all registered tools and memory integration.
        The graph is cached until tools are modified to avoid rebuilding.
        Usage: `graph = await agent_service.get_graph()` -> ready for agent tasks
        """
        if self._graph is None:
            self._graph = await self.build()
        return self._graph
