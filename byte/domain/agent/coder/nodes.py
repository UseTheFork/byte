from typing import TYPE_CHECKING, List

from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode

from byte.domain.agent.coder.prompts import coder_prompt
from byte.domain.agent.coder.state import CoderState

if TYPE_CHECKING:
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.tools import BaseTool

    from byte.container import Container


async def create_coder_node(container: "Container") -> callable:
    """Create the coder agent node specialized for software development tasks.

    Returns a node function that uses the LLM with coding-specific prompts
    and context to provide expert software engineering assistance. Always
    integrates file context and project structure for enhanced responses.
    Usage: `coder_node = create_coder_node(container)` -> LangGraph node function
    """

    # Pre-resolve services during node creation
    llm_service = await container.make("llm_service")
    file_service = await container.make("file_service")

    async def coder_node(state: CoderState) -> dict:
        """Coder agent node that processes coding requests and generates responses.

        Uses the configured LLM with coding-specific system prompt and context
        to analyze user requests and either call tools or provide direct coding
        assistance. Always includes comprehensive file and project context.
        """

        # Get LLM (tools will be bound by graph builder)
        llm: BaseChatModel = llm_service.get_main_model()

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
        response = llm.invoke(prompt_messages)

        return {"messages": [response]}

    return coder_node


def create_tool_node(tools: List["BaseTool"]) -> ToolNode:
    """Create a tool execution node for coder-specific tools.

    Handles execution of coding tools like file operations, code analysis,
    testing, and documentation generation with proper error handling.
    Usage: `tool_node = create_tool_node(tools)` -> LangGraph tool executor
    """
    return ToolNode(tools)


def should_continue(state: CoderState) -> str:
    """Conditional edge function for coder agent flow control.

    Determines whether to continue with tool calls or provide final response
    based on the agent's decision. Implements the ReAct pattern for iterative
    problem-solving in coding tasks.
    Usage: Used as conditional edge in StateGraph routing
    """
    messages = state["messages"]
    last_message = messages[-1]

    # If the last message has tool calls, route to tools
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    # Otherwise, we're done and should end
    return "end"
