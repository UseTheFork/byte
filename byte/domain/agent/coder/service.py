from typing import Annotated, Type

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict

from byte.core.response.handler import ResponseHandler
from byte.domain.agent.base import BaseAgent
from byte.domain.agent.coder.prompts import coder_prompt, watch_prompt
from byte.domain.files.events import CompletionRequested
from byte.domain.files.service import FileService
from byte.domain.llm.service import LLMService
from byte.domain.memory.service import MemoryService
from byte.domain.tools.file_operations import replace_text_in_file
from byte.domain.ui.tools import user_confirm, user_input, user_select


class CoderState(TypedDict):
    """Coder-specific state with file context."""

    messages: Annotated[list[AnyMessage], add_messages]
    file_context: str


class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    async def __call__(self, state: CoderState, config: RunnableConfig):
        print("here")
        while True:
            # configuration = config.get("configurable", {})
            # passenger_id = configuration.get("passenger_id", None)
            # state = {**state, "file_context": passenger_id}
            result = self.runnable.invoke(state, config=config)
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


class CoderAgent(BaseAgent):
    """Domain service for the coder agent specialized in software development.

    Orchestrates coding assistance through LangGraph-based agent with
    specialized tools, file context integration, and conversation memory.
    Optimized for code generation, debugging, refactoring, and analysis.
    Usage: `coder_service.stream_code("Fix this bug", thread_id)` -> streaming response
    """

    name: str = "coder"

    def get_state_class(self) -> Type[TypedDict]:  # pyright: ignore[reportInvalidTypeForm]
        """Return coder-specific state class."""
        return CoderState

    def get_tools(self):
        return [user_confirm, user_select, user_input, replace_text_in_file]

    async def execute_watch_request(self, event: CompletionRequested) -> None:
        """ """
        await self.execute(watch_prompt)

    async def execute(self, args: str) -> None:
        """Execute coder request and stream response to console.

        Processes the user's coding request through the coder agent,
        streaming the response in real-time for immediate feedback.
        Usage: Called by command processor when user types `/coder <request>`
        """

        coder_service = await self.make(CoderAgent)
        response_handler = await self.make(ResponseHandler)

        # Stream coder agent response through centralized handler
        await response_handler.handle_stream(coder_service.stream(args))

    async def build(self) -> "CompiledStateGraph":
        """Build and compile the coder agent graph with memory and tools.

        Creates a StateGraph optimized for coding tasks with specialized
        prompts, file context integration, and development-focused routing.
        Usage: `graph = await builder.build()` -> ready for coding assistance
        """

        llm_service = await self.make(LLMService)
        llm: BaseChatModel = llm_service.get_main_model()

        assistant_runnable = coder_prompt | llm.bind_tools(self.get_tools())

        State = self.get_state_class()

        # Create the state graph with coder-specific state
        graph = StateGraph(State)

        # Create specialized nodes
        # coder_node = await self.create_coder_node()
        tool_node = ToolNode(self.get_tools())

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
        memory_service = await self.make(MemoryService)
        checkpointer = await memory_service.get_saver()

        # Compile graph with memory and configuration
        return graph.compile(checkpointer=checkpointer, debug=False)

    async def get_file_context(self, state: CoderState):
        """Foo"""
        file_service: FileService = await self.make(FileService)
        initial_file_context = file_service.generate_context_prompt()

        return {"file_context": initial_file_context}

    async def should_continue(self, state: CoderState) -> str:
        """Conditional edge function for coder agent flow control."""
        messages = state["messages"]
        last_message = messages[-1]

        # If the last message has tool calls, route to tools
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"

        return "end"
