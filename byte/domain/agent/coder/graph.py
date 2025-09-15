from typing import TYPE_CHECKING, List

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from byte.domain.agent.coder.nodes import create_coder_node, should_continue
from byte.domain.agent.coder.state import CoderState

if TYPE_CHECKING:
    from langchain_core.tools import BaseTool
    from langgraph.graph.state import CompiledStateGraph

    from byte.container import Container


class CoderGraphBuilder:
    """Builder for the coder agent LangGraph implementation.

    Constructs a specialized coding agent graph with software development
    tools, file context integration, and conversation memory. Optimized
    for code generation, analysis, debugging, and refactoring tasks.
    Usage: `builder = CoderGraphBuilder(container, tools).build()` -> compiled graph
    """

    def __init__(self, container: "Container", tools: List["BaseTool"]):
        self.container = container
        self.tools = tools

    async def build(self) -> "CompiledStateGraph":
        """Build and compile the coder agent graph with memory and tools.

        Creates a StateGraph optimized for coding tasks with specialized
        prompts, file context integration, and development-focused routing.
        Usage: `graph = await builder.build()` -> ready for coding assistance
        """
        # Create the state graph with coder-specific state
        graph = StateGraph(CoderState)

        # Create specialized nodes
        coder_node = await create_coder_node(self.container)
        tool_node = ToolNode(self.tools)

        # Add nodes to graph
        graph.add_node("coder", coder_node)
        graph.add_node("tools", tool_node)

        # Set entry point to coder
        graph.add_edge(START, "coder")

        # Add conditional routing from coder
        graph.add_conditional_edges(
            "coder",
            should_continue,
            {
                "tools": "tools",  # If tool calls, execute tools
                "end": END,  # If no tool calls, end conversation
            },
        )

        # After tools, always return to coder for analysis
        graph.add_edge("tools", "coder")

        # Get memory service for conversation persistence
        memory_service = await self.container.make("memory_service")
        checkpointer = await memory_service.get_saver()

        # Get coder configuration
        config_service = await self.container.make("config")
        coder_config = config_service.config.coder

        # Compile graph with memory and configuration
        return graph.compile(
            checkpointer=checkpointer,
            interrupt_before=["tools"] if coder_config.interrupt_before_tools else None,
            debug=config_service.config.app.debug,
        )
