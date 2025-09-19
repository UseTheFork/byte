from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Annotated, Optional, Type, TypedDict

from langchain_core.messages import HumanMessage
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.graph.state import CompiledStateGraph, Runnable, RunnableConfig

from byte.core.config.mixins import Configurable
from byte.core.service.mixins import Bootable, Injectable
from byte.domain.events.mixins import Eventable
from byte.domain.memory.service import MemoryService

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph


class BaseState(TypedDict):
    """Base state that all agents inherit."""

    messages: Annotated[list[AnyMessage], add_messages]


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


class BaseAgent(ABC, Bootable, Configurable, Injectable, Eventable):
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
        if thread_id is None:
            memory_service = await self.make(MemoryService)
            thread_id = memory_service.create_thread()

        # Create configuration with thread ID
        config = RunnableConfig(
            configurable={"thread_id": thread_id, "container": self.container}
        )

        State = self.get_state_class()

        initial_state = State(messages=[HumanMessage(content=request)])

        # Get the graph and stream coder responses with token-level streaming
        graph = await self.get_graph()
        async for events in graph.astream_events(initial_state, config, version="v2"):
            yield events

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
