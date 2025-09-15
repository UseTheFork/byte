from typing import Annotated, Sequence

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


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
