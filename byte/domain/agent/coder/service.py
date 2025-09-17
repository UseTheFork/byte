from typing import TYPE_CHECKING, Annotated, List, Optional

from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict

from byte.context import make
from byte.core.config.mixins import Configurable
from byte.core.events.mixins import Eventable
from byte.core.service.mixins import Bootable
from byte.domain.agent.coder.prompts import coder_prompt
from byte.domain.files.service import FileService
from byte.domain.memory.service import MemoryService
from byte.domain.ui.tools import user_confirm, user_input, user_select

if TYPE_CHECKING:
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.tools import BaseTool
    from langgraph.graph.state import CompiledStateGraph

    from byte.container import Container


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    file_context: str


class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    async def __call__(self, state: State, config: RunnableConfig):
        while True:
            # configuration = config.get("configurable", {})
            # passenger_id = configuration.get("passenger_id", None)
            # state = {**state, "file_context": passenger_id}
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
            self._graph = await self.build()
        return self._graph

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
        config = RunnableConfig(configurable={"thread_id": thread_id})

        initial_state = State(messages=[HumanMessage(content=request)])

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

        llm_service = await make("llm_service")
        llm: BaseChatModel = llm_service.get_main_model()
        # llm_with_tools = llm.bind_tools(self._tools)

        assistant_runnable = coder_prompt | llm.bind_tools(self._tools)

        # Create the state graph with coder-specific state
        graph = StateGraph(State)

        # Create specialized nodes
        # coder_node = await self.create_coder_node()
        tool_node = ToolNode(self._tools)

        # Add nodes to graph
        graph.add_node("fetch_file_context", self.get_file_context)
        graph.add_node("coder", Assistant(assistant_runnable))
        graph.add_node("tools", tool_node)

        # Set entry point to coder
        graph.add_edge(START, "fetch_file_context")
        graph.add_edge("fetch_file_context", "coder")

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

    async def get_file_context(self, state: State):
        """Foo"""
        file_service: FileService = await make("file_service")
        initial_file_context = file_service.generate_context_prompt()

        return {"file_context": initial_file_context}

    async def should_continue(self, state: State) -> str:
        """Conditional edge function for coder agent flow control."""
        messages = state["messages"]
        last_message = messages[-1]

        # If the last message has tool calls, route to tools
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"

        return "end"
