from typing import Any, Dict

from pydantic import BaseModel, Field


class LLMModelConfig(BaseModel):
    """Configuration for a specific LLM model."""

    model: str = Field(default="", description="The model identifier to use")
    provider: str = Field(default="", description="The models provider to use")
    extra_params: Dict[str, Any] = Field(
        default_factory=dict, description="Additional parameters to pass to the model initialization"
    )


class LLMConfig(BaseModel):
    """LLM domain configuration with provider-specific settings."""

    fast: LLMModelConfig = LLMModelConfig()
    standard: LLMModelConfig = LLMModelConfig()
    reasoning: LLMModelConfig = LLMModelConfig()
    coding: LLMModelConfig = LLMModelConfig()
