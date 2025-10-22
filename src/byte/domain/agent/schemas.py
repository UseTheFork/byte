from typing import List, Literal, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import BasePromptTemplate
from langchain_core.tools import BaseTool
from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class AssistantContextSchema:
	"""Configuration for agent assistant including LLM, runnable chain, and tools.

	Different agents provide different components based on their needs:
	- All agents provide the runnable (prompt | llm chain)
	- Ask agent provides tools for ToolNode
	- All agents provide main and weak llm references for different operations
	- All agents provide their class name for identification
	- Mode indicates whether the runnable uses main or weak AI

	Usage: `config = await agent.get_assistant_runnable()`
	Usage: `AssistantNode(runnable=config.runnable)`
	Usage: `ToolNode(tools=config.tools) if config.tools else None`
	"""

	mode: Literal["main", "weak"]  # Which model the runnable uses
	prompt: BasePromptTemplate  # The prompt | llm chain to execute
	main: BaseChatModel  # Reference to the main LLM for complex reasoning
	weak: BaseChatModel  # Reference to the weak LLM for simple operations
	agent: str  # Agent class name for identification
	tools: Optional[List[BaseTool]] = Field(default=None)  # Tools bound to LLM, if any


@dataclass
class TokenUsageSchema:
	"""Token usage tracking for LLM interactions.

	Tracks input, output, and total tokens consumed during LLM operations.

	Usage: `usage = TokenUsageSchema(input_tokens=2897, output_tokens=229, total_tokens=3126)`
	"""

	input_tokens: int = 0
	output_tokens: int = 0
	total_tokens: int = 0
