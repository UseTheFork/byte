from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional

from langgraph.graph.state import CompiledStateGraph, RunnableConfig

from byte.memory import MemoryService
from byte.orchestration import BaseState
from byte.support import Str
from byte.support.mixins import Bootable, Configurable, Eventable
from byte.tui import TUIManagerService

if TYPE_CHECKING:
    from byte.orchestration import PhaseModel


class BaseWorkflow(ABC, Bootable, Eventable, Configurable):
    """ """

    _graph: Optional[CompiledStateGraph] = None

    @property
    def name(self) -> str:
        """Workflow Name"""
        return Str.class_to_snake_case(self.__class__.__name__)

    @property
    def human_name(self) -> str:
        """Human readable workflow name"""
        return Str.snake_to_title(self.name).strip()

    @abstractmethod
    def get_phases(self) -> List[PhaseModel] | None: ...

    @abstractmethod
    async def build(self) -> CompiledStateGraph:
        """Build and compile the agent graph with memory and tools.

        Must be implemented by subclasses to define their specific agent
        behavior, routing logic, and tool integration patterns.
        Usage: Override in subclass to create domain-specific agent graphs
        """
        ...

    async def compile(
        self, request: dict, thread_id: Optional[str] = None
    ) -> tuple[CompiledStateGraph, BaseState, RunnableConfig]:
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

        tui_manager_service = self.app.make(TUIManagerService)
        panel_id = tui_manager_service.get_panel_id()

        # Create configuration with thread ID
        config = RunnableConfig(
            configurable={"thread_id": thread_id}, metadata={"panel_id": panel_id, "workflow": self.name}
        )

        # Create initial state using the agent's state class
        initial_state = BaseState(**request)  # ty:ignore[missing-typed-dict-key]

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
