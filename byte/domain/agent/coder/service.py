from typing import TYPE_CHECKING, Annotated, List, Optional, Sequence

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict

from byte.context import make
from byte.core.config.configurable import Configurable
from byte.core.events.eventable import Eventable
from byte.core.mixins.bootable import Bootable
from byte.domain.agent.coder.prompts import coder_prompt
from byte.domain.memory.service import MemoryService
from byte.domain.ui.tools import user_confirm, user_input, user_select

if TYPE_CHECKING:
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.tools import BaseTool
    from langgraph.graph.state import CompiledStateGraph

    from byte.container import Container


class CoderState(TypedDict):
    """State schema for the coder agent specialized for coding tasks.

    Extends the standard MessagesState pattern with coding-specific context
    like file information, project structure, and code analysis results.
    Optimized for software development workflows and code generation.
    Usage: Standard LangGraph state for coding-focused tool-calling agent
    """

    # Core message history with automatic message management
    messages: Annotated[Sequence[BaseMessage], add_messages]

    # Coding-specific context
    file_context: str  # Current files in context from FileService
    project_structure: str  # Project layout and organization
    code_analysis: str  # Static analysis results and insights


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
        self._tools: List[BaseTool] = [user_confirm, user_select, user_input]

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
        """Create and configure the coder agent graph."""
        return await self.build()

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
            memory_service: MemoryService = await make("memory_service")
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
        async for events in graph.astream_events(initial_state, config, version="v2"):
            yield events

    async def build(self) -> "CompiledStateGraph":
        """Build and compile the coder agent graph with memory and tools.

        Creates a StateGraph optimized for coding tasks with specialized
        prompts, file context integration, and development-focused routing.
        Usage: `graph = await builder.build()` -> ready for coding assistance
        """

        # Create the state graph with coder-specific state
        graph = StateGraph(CoderState)

        # Create specialized nodes
        coder_node = await self.create_coder_node()
        tool_node = ToolNode(self._tools)

        # Add nodes to graph
        graph.add_node("coder", coder_node)
        graph.add_node("tools", tool_node)

        # Set entry point to coder
        graph.add_edge(START, "coder")

        # Add conditional routing from coder
        graph.add_conditional_edges(
            "coder",
            self.should_continue,
            {
                "tools": "tools",  # If tool calls, execute tools
                "end": END,  # If no tool calls, end conversation
            },
        )

        # After tools, always return to coder for analysis
        graph.add_edge("tools", "coder")

        # Get memory service for conversation persistence
        memory_service = await make("memory_service")
        checkpointer = await memory_service.get_saver()

        # Compile graph with memory and configuration
        return graph.compile(checkpointer=checkpointer, debug=False)

    async def create_coder_node(self) -> callable:
        """Create the coder agent node specialized for software development tasks."""
        # Pre-resolve services during node creation
        llm_service = await make("llm_service")
        file_service = await make("file_service")

        async def coder_node(state: CoderState) -> dict:
            """Coder agent node that processes coding requests and generates responses."""
            # Get LLM with tools bound
            llm: BaseChatModel = llm_service.get_main_model()
            llm_with_tools = llm.bind_tools(self._tools)

            # Build enhanced context for coding tasks
            messages = list(state["messages"])

            # Always add file context for coding assistance
            file_context = file_service.generate_context_prompt()
            if file_context.strip():
                # Add file context as system message
                context_message = SystemMessage(
                    content=f"## Current File Context:\n{file_context}"
                )
                messages.insert(0, context_message)

            # Apply coder-specific system prompt
            prompt_messages = coder_prompt.format_messages(messages=messages)

            # Invoke LLM with coding context
            response = await llm_with_tools.ainvoke(prompt_messages)

            return {"messages": [response]}

        return coder_node

    def should_continue(self, state: CoderState) -> str:
        """Conditional edge function for coder agent flow control."""
        messages = state["messages"]
        last_message = messages[-1]

        # If the last message has tool calls, route to tools
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"

        return "end"
