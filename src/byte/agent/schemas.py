from typing import TYPE_CHECKING, List, Literal, Optional

from langchain.chat_models import BaseChatModel
from langchain.tools import BaseTool
from langchain_core.prompts import BasePromptTemplate
from pydantic import Field
from pydantic.dataclasses import dataclass

if TYPE_CHECKING:
    pass


@dataclass
class MetadataSchema:
    """Metadata tracking for agent execution state.

    Tracks execution metrics like current loop iteration for monitoring and debugging.

    Usage: `metadata = MetadataSchema(iteration=1)`
    """

    iteration: int = Field(default=0)
    erase_history: bool = Field(default=False)


@dataclass
class ConstraintSchema:
    """User-defined constraint to guide agent behavior during execution.

    Constraints are suggestions or actions the agent should avoid or follow based on
    user feedback, such as declined tool calls or rejected suggestions.

    Usage: `constraint = ConstraintSchema(type="avoid", description="Do not suggest using ripgrep_search")`
    Usage: `constraint = ConstraintSchema(type="require", description="Always use type hints", source="user_input")`
    """

    type: Literal["avoid", "require"]  # Whether this is something to avoid or something required
    description: str  # Human-readable constraint description
    source: Optional[str] = Field(default=None)  # Where the constraint originated (e.g., "declined_tool", "user_input")


@dataclass
class AgentConfigSchema:
    """Base schema for agent configuration settings."""

    name: str  # Human-readable name of the setting
    description: str  # Human-readable description of the setting


@dataclass
class AgentConfigBoolSchema(AgentConfigSchema):
    """Boolean configuration setting for agents."""

    value: bool = Field(default=False)


@dataclass
class AgentConfigStringSchema(AgentConfigSchema):
    """String configuration setting for agents."""

    value: str = Field(default="")


@dataclass
class PromptSettingsSchema:
    """Settings for controlling prompt behavior and content.

    Boolean flags to enable or disable specific prompt features.

    Usage: `settings = PromptSettingsSchema(has_project_hierarchy=True)`
    """

    has_project_hierarchy: bool = Field(default=False)


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

    mode: Literal["main", "weak", "none"]  # Which model the runnable uses
    prompt: BasePromptTemplate | None  # The prompt | llm chain to execute
    main: BaseChatModel | None  # Reference to the main LLM for complex reasoning
    weak: BaseChatModel | None  # Reference to the weak LLM for simple operations
    agent: str  # Agent class name for identification
    prompt_settings: PromptSettingsSchema = Field(default_factory=PromptSettingsSchema)  # Settings for prompt behavior
    tools: Optional[List[BaseTool]] = Field(default=None)  # Tools bound to LLM, if any
    enforcement: Optional[List[str]] = Field(default=None)
    recovery_steps: Optional[str] = Field(default=None)


@dataclass
class TokenUsageSchema:
    """Token usage tracking for LLM interactions.

    Tracks input, output, and total tokens consumed during LLM operations.

    Usage: `usage = TokenUsageSchema(input_tokens=2897, output_tokens=229, total_tokens=3126)`
    """

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
