from typing import Any, Dict

from pydantic import BaseModel, Field


class LLMModelConfig(BaseModel):
    """Configuration for a specific LLM model."""

    model: str = Field(default="", description="The model identifier to use")
    extra_params: Dict[str, Any] = Field(
        default_factory=dict, description="Additional parameters to pass to the model initialization"
    )


class LLMProviderConfig(BaseModel):
    """Configuration for a specific LLM provider."""

    enable: bool = Field(default=False, description="Whether this LLM provider is enabled and available for use")
    api_key: str = Field(default="", description="API key for authenticating with the LLM provider", exclude=True)
    extra_params: Dict[str, Any] = Field(
        default_factory=dict, description="Additional parameters to pass to the model initialization"
    )


class ProvidersConfig(BaseModel):
    """Configuration for all LLM providers."""

    gemini: LLMProviderConfig = LLMProviderConfig()
    anthropic: LLMProviderConfig = LLMProviderConfig()
    openai: LLMProviderConfig = LLMProviderConfig()


class LLMConfig(BaseModel):
    """LLM domain configuration with provider-specific settings."""

    main_model: LLMModelConfig = LLMModelConfig()
    weak_model: LLMModelConfig = LLMModelConfig()

    providers: ProvidersConfig = ProvidersConfig()
