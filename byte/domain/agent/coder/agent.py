from typing import Annotated, Type

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict

from byte.domain.agent.base import Agent
from byte.domain.agent.coder.command_parser import CommandParser
from byte.domain.agent.coder.command_validator import CommandValidator
from byte.domain.agent.coder.commands import AddFileCommand, ReplaceTextCommand
from byte.domain.agent.coder.prompts import coder_prompt
from byte.domain.files.service.file_service import FileService
from byte.domain.llm.service.llm_service import LLMService
from byte.domain.memory.service import MemoryService


class CoderState(TypedDict):
    """Coder-specific state with file context."""

    messages: Annotated[list[AnyMessage], add_messages]
    file_context: str
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
        return []
        # return [user_confirm, user_select, user_input, replace_text_in_file]

    async def build(self) -> CompiledStateGraph:
        """Build and compile the coder agent graph with memory and tools."""

        llm_service = await self.make(LLMService)
        llm: BaseChatModel = llm_service.get_main_model()

        # Create the assistant runnable
        assistant_runnable = coder_prompt | llm.bind_tools(self.get_tools())

        # Create the state graph
        graph = StateGraph(self.get_state_class())

        # Add nodes
        graph.add_node("fetch_file_context", self._get_file_context)
        graph.add_node("assistant", self._create_assistant_node(assistant_runnable))
        graph.add_node("parse_commands", self._parse_commands)
        graph.add_node("validate_commands", self._validate_commands)
        graph.add_node("tools", ToolNode(self.get_tools()))

        # Define edges
        graph.add_edge(START, "fetch_file_context")
        graph.add_edge("fetch_file_context", "assistant")
        graph.add_edge("assistant", "parse_commands")
        graph.add_edge("parse_commands", "validate_commands")

        # Conditional routing from validate_commands
        graph.add_conditional_edges(
            "validate_commands",
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

    async def _get_file_context(self, state: CoderState) -> dict:
        """Fetch current file context for the agent."""

        file_service: FileService = await self.make(FileService)
        file_context = file_service.generate_context_prompt()
        return {"file_context": file_context}

    async def _parse_commands(self, state: CoderState) -> dict:
        """Parse commands from the last assistant message."""
        messages = state["messages"]
        last_message = messages[-1]

        # Get the content from the last message
        content = ""
        if hasattr(last_message, "content"):
            if isinstance(last_message.content, str):
                content = last_message.content
            elif isinstance(last_message.content, list):
                # Handle list content (like from some LLM providers)
                content = "".join(
                    [
                        item.get("text", "") if isinstance(item, dict) else str(item)
                        for item in last_message.content
                    ]
                )

        # Parse commands using the command parser
        parser = CommandParser()
        try:
            parsed_commands = parser.parse_commands(content)

            # Convert Pydantic models to serializable format for state storage
            return {
                "parsed_commands": [
                    {
                        "command": cmd.command,
                        "model_data": cmd.dict(),  # Store full Pydantic model data
                        "model_type": cmd.__class__.__name__,
                    }
                    for cmd in parsed_commands
                ]
            }
        except ValueError as e:
            # Store parsing errors in state for handling
            return {"parsed_commands": [], "parsing_errors": [str(e)]}

    async def _validate_commands(self, state: CoderState) -> dict:
        """Validate parsed commands before execution."""
        parsed_commands_data = state.get("parsed_commands", [])
        parsing_errors = state.get("parsing_errors", [])

        # If there were parsing errors, return them immediately
        if parsing_errors:
            return {"validation_errors": parsing_errors}

        # Reconstruct Pydantic models from stored data

        MODEL_REGISTRY = {
            "ReplaceTextCommand": ReplaceTextCommand,
            "AddFileCommand": AddFileCommand,
        }

        commands = []
        reconstruction_errors = []

        for cmd_data in parsed_commands_data:
            try:
                model_type = cmd_data.get("model_type")
                model_class = MODEL_REGISTRY.get(model_type)

                if not model_class:
                    reconstruction_errors.append(f"Unknown command type: {model_type}")
                    continue

                # Reconstruct the Pydantic model
                command = model_class(**cmd_data["model_data"])
                commands.append(command)

            except Exception as e:
                reconstruction_errors.append(f"Failed to reconstruct command: {e}")

        if reconstruction_errors:
            return {"validation_errors": reconstruction_errors}

        # Get file service for validation
        file_service: FileService = await self.make(FileService)
        validator = CommandValidator(file_service)

        # Validate all commands
        validation_errors = await validator.validate_commands(commands)

        return {"validation_errors": validation_errors}

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
        """Determine next step based on validation results and tool calls."""
        messages = state["messages"]
        last_message = messages[-1]

        # Route to tools if there are tool calls
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"

        # Check validation errors
        validation_errors = state.get("validation_errors", [])
        if validation_errors:
            # If there are validation errors, end with error information
            # In the future, this could route back to assistant for correction
            return "end"

        # Check if we have valid parsed commands to execute
        parsed_commands = state.get("parsed_commands", [])
        if parsed_commands:
            # For now, just end - in the future this could route to command execution
            return "end"

        return "end"
