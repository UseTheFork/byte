from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph, RunnableConfig

from byte.memory import MemoryService
from byte.orchestration import BaseState
from byte.support import Str
from byte.support.mixins import Bootable, Configurable, Eventable
from byte.tui import TUIManagerService

if TYPE_CHECKING:
    from byte.orchestration import PhaseModel, RoutePhaseModel


class BaseWorkflow(ABC, Bootable, Eventable, Configurable):
    """Manage workflow execution with phases, routing, and state management."""

    _graph: Optional[CompiledStateGraph] = None

    @property
    def name(self) -> str:
        """Get the workflow name."""
        return Str.class_to_snake_case(self.__class__.__name__)

    @property
    def human_name(self) -> str:
        """Get the human-readable workflow name."""
        return Str.snake_to_title(self.name).strip()

    @abstractmethod
    def get_phases(self, **kwargs) -> List[PhaseModel | RoutePhaseModel] | None: ...

    @abstractmethod
    async def build(self) -> CompiledStateGraph:
        """Build and compile the agent graph with memory and tools."""
        ...

    async def compile(
        self, request: dict, thread_id: Optional[str] = None
    ) -> tuple[CompiledStateGraph, BaseState, RunnableConfig]:
        """Compile the workflow with request data and optional thread ID."""
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

    async def get_checkpointer(self) -> InMemorySaver:
        """Get the memory saver for persistence."""
        memory_service = self.app.make(MemoryService)
        checkpointer = await memory_service.get_saver()
        return checkpointer

    async def get_graph(self) -> CompiledStateGraph:
        """Get or create the compiled agent graph."""
        if self._graph is None:
            self._graph = await self.build()
        return self._graph
