from abc import abstractmethod
from typing import List, Optional

from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.memory import MemoryService
from byte.node import Node
from byte.orchestration import AssistantContextSchema, BaseState, DummyNodeReachedException


class BaseAgent(Node):
    _graph: Optional[CompiledStateGraph] = None

    def get_enforcement(self) -> List[str]:
        return []

    @abstractmethod
    def get_user_template(self) -> List[str]:
        """Get the user message template for this agent.

        Must be implemented by subclasses to return their specific user message
        template, which defines how user requests are formatted in prompts.
        Usage: Override in subclass to provide domain-specific user message formatting
        """
        pass

    @abstractmethod
    def get_prompt(self):
        """Get the ChatPromptTemplate for this agent.

        Must be implemented by subclasses to return their specific ChatPromptTemplate,
        which defines the overall prompt structure including system and user messages.
        Usage: Override in subclass to provide domain-specific prompt templates
        """
        pass

    @abstractmethod
    async def build(self) -> CompiledStateGraph:
        """Build and compile the agent graph with memory and tools.

        Must be implemented by subclasses to define their specific agent
        behavior, routing logic, and tool integration patterns.
        Usage: Override in subclass to create domain-specific agent graphs
        """
        pass

    async def get_checkpointer(self):
        # Get memory for persistence
        memory_service = self.app.make(MemoryService)
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

    async def __call__(
        self, state: BaseState, config: RunnableConfig, runtime: Runtime[AssistantContextSchema]
    ) -> Command[str]:
        raise DummyNodeReachedException(
            "Reached dummy node during execution. This indicates a routing error in the agent graph."
        )
