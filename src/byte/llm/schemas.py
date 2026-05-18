from enum import StrEnum
from typing import Any, Dict

from pydantic import BaseModel, Field


class ReinforcementMode(StrEnum):
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

    cache_write_input_token_cost: float = 0
    cache_read_input_token_cost: float = 0


class ModelBehavior(BaseModel):
    """Behavioral configuration for model prompt engineering and output handling.

    Defines ByteSmith-specific behaviors that control how prompts are constructed
    and how the model is guided, separate from LangChain model parameters.
    Usage: `behavior = ModelBehavior(reinforcement_mode=ReinforcementMode.EAGER)`
    """

    reinforcement_mode: ReinforcementMode = ReinforcementMode.NONE


class ModelSchema(BaseModel):
    """Configuration for the main LLM model used for primary tasks."""

    model: str = ""
    provider: str = ""
    constraints: ModelConstraints = Field(default_factory=ModelConstraints)
    behavior: ModelBehavior = Field(default_factory=ModelBehavior)
    extra_params: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters to pass to the model")
