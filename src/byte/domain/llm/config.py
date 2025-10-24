import os
from typing import Any, Dict, Literal

from pydantic import BaseModel, Field


class LLMProviderConfig(BaseModel):
	"""Configuration for a specific LLM provider."""

	enabled: bool = Field(default=False, description="Whether this LLM provider is enabled and available for use")
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

	def model_post_init(self, __context):
		"""Initialize LLM config with automatic API key detection from environment.

		Usage: `llm_config = LLMConfig()`
		"""

		# Auto-detect and configure Anthropic
		anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
		if anthropic_key:
			# Preserve existing model_params if anthropic was already configured
			existing_model_params = self.anthropic.model_params if self.anthropic else {}
			self.anthropic = LLMProviderConfig(enabled=True, api_key=anthropic_key, model_params=existing_model_params)

		# Auto-detect and configure Gemini
		gemini_key = os.getenv("GEMINI_API_KEY", "")
		if gemini_key:
			# Preserve existing model_params if gemini was already configured
			existing_model_params = self.gemini.model_params if self.gemini else {}
			self.gemini = LLMProviderConfig(enabled=True, api_key=gemini_key, model_params=existing_model_params)

		# Auto-detect and configure OpenAI
		openai_key = os.getenv("OPENAI_API_KEY", "")
		if openai_key:
			# Preserve existing model_params if openai was already configured
			existing_model_params = self.openai.model_params if self.openai else {}
			self.openai = LLMProviderConfig(enabled=True, api_key=openai_key, model_params=existing_model_params)

		# Validate that at least one provider is configured
		if not (self.anthropic.enabled or self.gemini.enabled or self.openai.enabled):
			raise ValueError(
				"Missing required API key. Please set at least one of: "
				"ANTHROPIC_API_KEY, GEMINI_API_KEY, or OPENAI_API_KEY environment variable."
			)
