from typing import Type

from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict

from byte.domain.agent.implementations.base import Agent
from byte.domain.agent.implementations.coder.edit_format.base import (
    EditFormat,
)
from byte.domain.agent.implementations.coder.edit_format.editblock_fenced import (
    BlockedFenceEditFormat,
)
from byte.domain.agent.implementations.coder.prompts import coder_prompt
from byte.domain.agent.nodes.assistant_node import AssistantNode
from byte.domain.agent.nodes.lint_node import LintNode
from byte.domain.agent.nodes.parse_blocks_node import ParseBlocksNode
from byte.domain.agent.nodes.setup_node import SetupNode
from byte.domain.agent.state import CoderState
from byte.domain.llm.service.llm_service import LLMService
from byte.domain.memory.service import MemoryService
from byte.domain.tools.user_confirm import user_confirm


class CoderAgent(Agent):
    """Domain service for the coder agent specialized in software development.

    Pure domain service that handles coding logic without UI concerns.
    Integrates with file context, memory, and development tools through
    the actor system for clean separation of concerns.
    """

    edit_format: EditFormat

    async def boot(self):
        # TODO: Need to figure out how to specify what what edit_format is currently running.

        self.edit_format = BlockedFenceEditFormat(self.container)
        await self.edit_format.ensure_booted()

    def get_state_class(self) -> Type[TypedDict]:  # pyright: ignore[reportInvalidTypeForm]
        """Return coder-specific state class."""
        return CoderState

    def get_tools(self):
        """Return tools available to the coder agent."""
        return [user_confirm]

    async def get_checkpointer(self):
        # Get memory for persistence
        memory_service = await self.make(MemoryService)
        checkpointer = await memory_service.get_saver()
        return checkpointer

    async def build(self) -> CompiledStateGraph:
        """Build and compile the coder agent graph with memory and tools."""

        # Create the assistant and runnable
        llm_service = await self.make(LLMService)
        llm: BaseChatModel = llm_service.get_main_model()
        assistant_runnable = coder_prompt | llm.bind_tools(self.get_tools())

        # Create the state graph
        graph = StateGraph(self.get_state_class())

        # Add nodes
        graph.add_node(
            "setup_coder", await self.make(SetupNode, edit_format=self.edit_format)
        )
        graph.add_node(
            "assistant", await self.make(AssistantNode, runnable=assistant_runnable)
        )
        graph.add_node(
            "parse_blocks",
            await self.make(ParseBlocksNode, edit_format=self.edit_format),
        )
        graph.add_node("lint", await self.make(LintNode))
        graph.add_node("tools", ToolNode(self.get_tools()))

        # Define edges
        graph.add_edge(START, "setup_coder")
        graph.add_edge("setup_coder", "assistant")
        graph.add_edge("assistant", "parse_blocks")

        graph.add_edge("parse_blocks", "lint")

        # Conditional routing from assistant
        graph.add_conditional_edges(
            "assistant",
            self._should_continue,
            {
                "tools": "tools",
                "parse_blocks": "parse_blocks",
            },
        )

        # Conditional routing from assistant
        graph.add_conditional_edges(
            "parse_blocks",
            self._should_continue,
            {
                "validation_error": "assistant",
                "valid": "lint",
            },
        )

        # After tools, return to assistant
        graph.add_edge("tools", "assistant")
        graph.add_edge("lint", END)

        checkpointer = await self.get_checkpointer()
        return graph.compile(checkpointer=checkpointer, debug=False)

    async def _should_continue(self, state: CoderState) -> str:
        """Determine next step based on last message."""
        messages = state["messages"]
        last_message = messages[-1]

        if state["agent_status"] == "validation_error":
            return "validation_error"

        if state["agent_status"] == "valid":
            return "valid"

        # Route to tools if there are tool calls
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"

        return "parse_blocks"
