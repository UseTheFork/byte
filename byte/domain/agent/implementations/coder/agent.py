from typing import Type

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict

from byte.domain.agent.implementations.base import Agent, BaseState
from byte.domain.agent.implementations.coder.edit_format.editblock_fenced import (
    edit_format_system,
)
from byte.domain.agent.implementations.coder.prompts import coder_prompt
from byte.domain.files.service.file_service import FileService
from byte.domain.llm.service.llm_service import LLMService
from byte.domain.memory.service import MemoryService
from byte.domain.tools.user_confirm import user_confirm


class CoderState(BaseState):
    """Coder-specific state with file context."""

    file_context: str
    edit_format_system: str
    fence_open: str
    fence_close: str

    parsed_commands: list
    parsing_errors: list
    validation_errors: list


class CoderAgent(Agent):
    """Domain service for the coder agent specialized in software development.

    Pure domain service that handles coding logic without UI concerns.
    Integrates with file context, memory, and development tools through
    the actor system for clean separation of concerns.
    """

    name: str = "coder"

    def get_state_class(self) -> Type[TypedDict]:  # pyright: ignore[reportInvalidTypeForm]
        """Return coder-specific state class."""
        return CoderState

    def get_tools(self):
        """Return tools available to the coder agent."""
        # return []
        return [user_confirm]

    async def build(self) -> CompiledStateGraph:
        """Build and compile the coder agent graph with memory and tools."""

        llm_service = await self.make(LLMService)
        llm: BaseChatModel = llm_service.get_main_model()

        # Create the assistant runnable
        assistant_runnable = coder_prompt | llm.bind_tools(self.get_tools())

        # Create the state graph
        graph = StateGraph(self.get_state_class())

        # Add nodes
        graph.add_node("setup_coder", self._setup_coder)
        graph.add_node("assistant", self._create_assistant_node(assistant_runnable))
        # graph.add_node("parse_commands", self._parse_commands)
        # graph.add_node("validate_commands", self._validate_commands)
        graph.add_node("tools", ToolNode(self.get_tools()))

        # Define edges
        graph.add_edge(START, "setup_coder")
        graph.add_edge("setup_coder", "assistant")
        graph.add_edge("assistant", END)
        # graph.add_edge("assistant", "parse_commands")
        # graph.add_edge("parse_commands", "validate_commands")

        # Conditional routing from assistant
        graph.add_conditional_edges(
            "assistant",
            self._should_continue,
            {
                "tools": "tools",
                "end": END,
            },
        )

        # After tools, return to assistant
        graph.add_edge("tools", "assistant")

        # Get memory for persistence
        memory_service = await self.make(MemoryService)
        checkpointer = await memory_service.get_saver()

        return graph.compile(checkpointer=checkpointer, debug=False)

    async def _setup_coder(self, state: CoderState) -> dict:
        """Fetch current file context for the agent."""

        file_service: FileService = await self.make(FileService)
        file_context = file_service.generate_context_prompt()
        return {
            "file_context": file_context,
            "edit_format_system": edit_format_system,
            "fence_open": "```",
            "fence_close": "```",
        }

    async def _parse_commands(self, state: CoderState) -> dict:
        """Parse commands from the last assistant message."""
        # messages = state["messages"]
        # last_message = messages[-1]

        pass

    async def _validate_commands(self, state: CoderState) -> dict:
        """Validate parsed commands before execution."""

        pass

        # return {"validation_errors": validation_errors}

    def _create_assistant_node(self, runnable: Runnable):
        """Create the assistant node function."""

        async def assistant_node(state: CoderState, config: RunnableConfig):
            while True:
                result = await runnable.ainvoke(state, config=config)

                # Ensure we get a real response
                if not result.tool_calls and (
                    not result.content
                    or (
                        isinstance(result.content, list)
                        and not result.content[0].get("text")
                    )
                ):
                    # Re-prompt for actual response
                    messages = state["messages"] + [
                        ("user", "Respond with a real output.")
                    ]
                    state = {**state, "messages": messages}
                else:
                    break

            return {"messages": [result]}

        return assistant_node

    async def _should_continue(self, state: CoderState) -> str:
        """Determine next step based on last message."""
        messages = state["messages"]
        last_message = messages[-1]

        # Route to tools if there are tool calls
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"

        return "end"
