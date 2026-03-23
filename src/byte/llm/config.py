from typing import Any, Dict

from pydantic import BaseModel, Field


class LLMModelConfig(BaseModel):
    """Configuration for a specific LLM model."""

    provider: str = Field(default="", description="The model provider to use")
    model: str = Field(default="", description="The model identifier to use")
    extra_params: Dict[str, Any] = Field(
        default_factory=dict, description="Additional parameters to pass to the model initialization"
    )


class LLMConfig(BaseModel):
    """LLM domain configuration with provider-specific settings."""

    reasoning_model: LLMModelConfig = LLMModelConfig()
    main_model: LLMModelConfig = LLMModelConfig()
    weak_model: LLMModelConfig = LLMModelConfig()
