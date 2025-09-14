import asyncio
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from langchain_core.messages import HumanMessage

from byte.core.config.configurable import Configurable
from byte.core.events.eventable import Eventable
from byte.core.mixins.bootable import Bootable
from byte.domain.coder.graph import CoderGraphBuilder
from byte.domain.coder.state import CoderState
from byte.domain.llm.service import LLMService
from byte.domain.memory.service import MemoryService

if TYPE_CHECKING:
    from langchain_core.tools import BaseTool
    from langgraph.graph.state import CompiledStateGraph

    from byte.container import Container


class CoderService(Bootable, Configurable, Eventable):
    """Domain service for the coder agent specialized in software development.

    Orchestrates coding assistance through LangGraph-based agent with
    specialized tools, file context integration, and conversation memory.
    Optimized for code generation, debugging, refactoring, and analysis.
    Usage: `coder_service.stream_code("Fix this bug", thread_id)` -> streaming response
    """

    def __init__(self, container: Optional["Container"] = None):
        self.container = container
        self._graph: Optional[CompiledStateGraph] = None
        self._tools: List[BaseTool] = []
        if container:
            asyncio.create_task(self._async_init())

    def register_tool(self, tool: "BaseTool") -> None:
        """Register a coding tool for use by the coder agent.

        Tools are automatically bound to the coder LLM and made available
        for coding tasks. Common tools include file operations, code analysis,
        testing, and documentation generation.
        Usage: `coder_service.register_tool(file_editor_tool)` -> tool available
        """
        self._tools.append(tool)
        # Invalidate cached graph to force rebuild with new tools
        self._graph = None

    async def get_graph(self) -> "CompiledStateGraph":
        """Get or create the coder agent graph with current tools.

        Lazy-loads the graph with all registered tools and memory integration.
        The graph is cached until tools are modified to avoid rebuilding.
        Usage: `graph = await coder_service.get_graph()` -> ready for coding tasks
        """
        if self._graph is None:
            self._graph = await self._create_graph()
        return self._graph

    async def _create_graph(self) -> "CompiledStateGraph":
        """Create and configure the coder agent graph.

        Binds tools to the LLM, builds the specialized coder graph,
        and configures memory persistence for conversation continuity.
        """
        # Bind tools to LLM for tool-calling
        if self._tools:
            llm_service: LLMService = await self.container.make("llm_service")
            llm = llm_service.get_main_model()

            # Apply coder-specific temperature if configured
            coder_config = self.config.coder
            if hasattr(llm, "temperature"):
                llm.temperature = coder_config.temperature

            # Bind tools to the LLM
            llm_with_tools = llm.bind_tools(self._tools)
            # Update the LLM service with tool-bound model
            llm_service._models["main"] = llm_with_tools

        # Build the coder graph
        builder = CoderGraphBuilder(self.container, self._tools)
        return await builder.build()

    async def stream_code(
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
            memory_service: MemoryService = await self.container.make("memory_service")
            thread_id = memory_service.create_thread()

        # Create configuration with thread ID
        config = {"configurable": {"thread_id": thread_id}}

        # Create initial state with coding request
        initial_state = CoderState(
            messages=[HumanMessage(content=request)],
            file_context="",
            project_structure="",
            code_analysis="",
        )

        # Get the graph and stream coder responses with token-level streaming
        graph = await self.get_graph()
        async for chunk in graph.astream(initial_state, config, stream_mode="messages"):
            yield chunk

    def list_tools(self) -> List[str]:
        """List all registered coding tools available to the coder agent.

        Usage: `tools = coder_service.list_tools()` -> available tool names
        """
        return [tool.name for tool in self._tools]

    def get_capabilities(self) -> Dict[str, Any]:
        """Get coder agent capabilities and configuration.

        Usage: `caps = coder_service.get_capabilities()` -> agent info
        """
        return {
            "tools": self.list_tools(),
            "max_iterations": self.config.coder.max_iterations,
            "temperature": self.config.coder.temperature,
        }
