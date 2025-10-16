from typing import Any, List, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import BaseTool
from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class AssistantRunnable:
	"""Configuration for agent assistant including LLM, runnable chain, and tools.

	Different agents provide different components based on their needs:
	- All agents provide the runnable (prompt | llm chain)
	- Ask agent provides tools for ToolNode
	- All agents provide llm reference for analytics and EndNode

	Usage: `config = await agent.get_assistant_runnable()`
	Usage: `AssistantNode(runnable=config.runnable)`
	Usage: `ToolNode(tools=config.tools) if config.tools else None`
	"""

	runnable: Any  # The prompt | llm chain to execute
	llm: BaseChatModel  # Reference to the base LLM
	tools: Optional[List[BaseTool]] = Field(default=None)  # Tools bound to LLM, if any
