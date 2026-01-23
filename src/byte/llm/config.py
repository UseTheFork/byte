from typing import Any, Dict, Literal

from pydantic import BaseModel, Field


class LLMProviderConfig(BaseModel):
    """Configuration for a specific LLM provider."""

    enable: bool = Field(default=False, description="Whether this LLM provider is enabled and available for use")
    api_key: str = Field(default="", description="API key for authenticating with the LLM provider", exclude=True)
    model_params: Dict[str, Any] = Field(
        default_factory=dict, description="Additional parameters to pass to the model initialization"
    )


class LLMConfig(BaseModel):
    """LLM domain configuration with provider-specific settings."""

    model: Literal["anthropic", "gemini", "openai"] = Field(
        default="anthropic", description="The LLM provider to use for AI operations"
    )

    gemini: LLMProviderConfig = LLMProviderConfig()
    anthropic: LLMProviderConfig = LLMProviderConfig()
    openai: LLMProviderConfig = LLMProviderConfig()
