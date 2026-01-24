from enum import Enum
from typing import Any, Dict, Optional, Type

from langchain.chat_models import BaseChatModel
from pydantic import BaseModel, Field


class ReinforcementMode(str, Enum):
    """Strategy for adding reinforcement messages to model prompts.

    Controls whether and how strongly to reinforce instructions to ensure
    the model follows guidelines and produces desired output format.
    """

    NONE = "none"
    LAZY = "lazy"
    EAGER = "eager"


class ModelConstraints(BaseModel):
    """Operational constraints and cost specifications for an LLM model.

    Defines the capacity limits and economic factors that constrain model usage,
    including token limits and per-token costs for various operations.
    Usage: `constraints = ModelConstraints(max_input_tokens=200000, max_output_tokens=64000)`
    """

    max_input_tokens: int = 0
    max_output_tokens: int = 0

    input_cost_per_token: float = 0
    output_cost_per_token: float = 0

    input_cost_per_token_cached: float = 0
    cache_read_input_token_cost: float = 0


class ModelParams(BaseModel):
    """Configuration parameters for LLM model initialization.

    Defines the runtime parameters used to configure and authenticate with
    an LLM model, including model selection and behavioral settings.
    Usage: `params = ModelParams(model="claude-sonnet-4-5", api_key="...", temperature=0.1)`
    """

    model: str = ""
    temperature: float = 0.1
    stream_usage: bool | None = None


class ModelBehavior(BaseModel):
    """Behavioral configuration for model prompt engineering and output handling.

    Defines ByteSmith-specific behaviors that control how prompts are constructed
    and how the model is guided, separate from LangChain model parameters.
    Usage: `behavior = ModelBehavior(reinforcement_mode=ReinforcementMode.EAGER)`
    """

    reinforcement_mode: ReinforcementMode = ReinforcementMode.NONE


class ModelProvider(BaseModel):
    """Configuration for an LLM provider with API credentials and parameters."""

    api_key: str = ""
    params: Dict[str, Any] = Field(default_factory=dict)


class ModelSchema(BaseModel):
    """Configuration for the main LLM model used for primary tasks."""

    model_class: Optional[Type[BaseChatModel]] = None
    params: ModelParams = Field(default_factory=ModelParams)
    constraints: ModelConstraints = Field(default_factory=ModelConstraints)
    behavior: ModelBehavior = Field(default_factory=ModelBehavior)
    provider: ModelProvider = Field(default_factory=ModelProvider)
    extra_params: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters to pass to the model")
