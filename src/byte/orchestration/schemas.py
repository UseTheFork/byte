from typing import List, Literal, Optional

from langchain.tools import BaseTool
from langchain_core.prompts import BasePromptTemplate
from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class PromptSettingsSchema:
    """Configure prompt behavior settings."""

    has_project_hierarchy: bool = Field(default=False)
    has_project_information_and_context: bool = Field(default=True)
    has_file_context: bool = Field(default=True)


@dataclass
class MetadataSchema:
    """Track metadata for agent execution state."""

    iteration: int = Field(default=0)
    erase_history: bool = Field(default=False)
    mode: Literal["main", "weak", "none"] = Field(default="main")
    prompt_settings: PromptSettingsSchema = Field(default_factory=PromptSettingsSchema)


@dataclass
class ConstraintSchema:
    """Define user constraints to guide agent behavior."""

    type: Literal["avoid", "require"]  # Whether this is something to avoid or something required
    description: str  # Human-readable constraint description
    source: Optional[str] = Field(default=None)  # Where the constraint originated (e.g., "declined_tool", "user_input")


@dataclass
class AgentConfigSchema:
    """Define base schema for agent configuration."""

    name: str  # Human-readable name of the setting
    description: str  # Human-readable description of the setting


@dataclass
class AgentConfigBoolSchema(AgentConfigSchema):
    """Define boolean configuration setting for agents."""

    value: bool = Field(default=False)


@dataclass
class AgentConfigStringSchema(AgentConfigSchema):
    """Define string configuration setting for agents."""

    value: str = Field(default="")


@dataclass
class AssistantContextSchema:
    """Configure assistant context with LLM, runnable, and tools."""

    mode: Literal["main", "weak", "reasoning", "none"]  # Which model the runnable uses
    prompt: BasePromptTemplate | None  # The prompt | llm chain to execute
    agent: str  # Agent class name for identification
    user_template: List[str]
    prompt_settings: PromptSettingsSchema = Field(default_factory=PromptSettingsSchema)  # Settings for prompt behavior
    tools: Optional[List[BaseTool]] = Field(default=None)  # Tools bound to LLM, if any
    enforcement: Optional[List[str]] = Field(default=None)


@dataclass
class TokenUsageSchema:
    """Track token usage for LLM interactions."""

    input_tokens: int = 0
    input_token_cache_read: int = 0
    input_token_cache_creation: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
