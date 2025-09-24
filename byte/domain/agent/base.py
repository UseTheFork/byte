from abc import ABC, abstractmethod
from typing import Optional

from langchain_core.runnables import RunnableSerializable

from byte.core.config.mixins import Configurable
from byte.core.service.mixins import Bootable, Injectable


class Agent(ABC, Bootable, Configurable, Injectable):
    """Base class for all agent services providing common graph management functionality.

    Defines the interface for agent services with lazy-loaded graph compilation,
    tool management, and memory integration. Subclasses must implement the build
    method to define their specific agent behavior and routing logic.
    Usage: `class MyAgent(BaseAgent): async def build(self): ...`
    """

    name: str = ""
    _graph: Optional[RunnableSerializable] = None

    @abstractmethod
    # TODO: Add what this returns
    async def build(self) -> RunnableSerializable:
        """Build and compile the agent graph with memory and tools.

        Must be implemented by subclasses to define their specific agent
        behavior, routing logic, and tool integration patterns.
        Usage: Override in subclass to create domain-specific agent graphs
        """
        pass

    async def stream(
        self,
        request: str,
        thread_id: Optional[str] = None,
    ):
        """Stream coder agent responses for real-time coding assistance.

        Yields partial responses as the agent processes coding requests,
        enabling responsive development workflows and progress indication.
        Always streams responses for optimal CLI user experience.
        Usage: `async for chunk in coder_service.stream_code(request): ...`
        """
        # Get or create thread ID
        # if thread_id is None:
        #     memory_service = await self.make(MemoryService)
        #     thread_id = memory_service.create_thread()

        # Create configuration with thread ID
        # config = RunnableConfig(configurable={"thread_id": thread_id})

        # Get the graph and stream coder responses with token-level streaming
        graph = await self.get_agent()
        async for events in graph.astream_events(
            request, include_types=["chat_model", "tool"]
        ):
            yield events

    def get_tools(self):
        return []

    async def get_agent(self):
        """Get or create the agent graph with current tools.

        Lazy-loads the graph with all registered tools and memory integration.
        The graph is cached until tools are modified to avoid rebuilding.
        Usage: `graph = await agent_service.get_graph()` -> ready for agent tasks
        """
        if self._graph is None:
            self._graph = await self.build()
        return self._graph
