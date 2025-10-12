from typing import Any

from langchain_core.language_models import BaseChatModel

from byte.core.service.base_service import Service
from byte.domain.llm.schemas import AnthropicSchema, GoogleSchema, LLMSchema, OpenAiSchema


class LLMService(Service):
	"""Base LLM service that all providers extend.

	Provides a unified interface for different LLM providers (OpenAI, Anthropic, etc.)
	with model caching and configuration management. Enables provider-agnostic
	AI functionality throughout the application.
	Usage: `service = OpenAILLMService(container)` -> provider-specific implementation
	"""

	_service_config: LLMSchema

	async def _configure_service(self) -> None:
		"""Configure LLM service with model settings based on global configuration."""

		if self._config.llm.model == "anthropic":
			self._service_config = AnthropicSchema(
				api_key=self._config.llm.anthropic.api_key,
				provider_params=self._config.llm.anthropic.model_params.copy(),
			)

		if self._config.llm.model == "openai":
			self._service_config = OpenAiSchema(
				api_key=self._config.llm.openai.api_key,
				provider_params=self._config.llm.openai.model_params.copy(),
			)

		if self._config.llm.model == "gemini":
			self._service_config = GoogleSchema(
				api_key=self._config.llm.gemini.api_key,
				provider_params=self._config.llm.gemini.model_params.copy(),
			)

	def get_model(self, model_type: str = "main", **kwargs) -> Any:
		"""Get a model instance with lazy initialization and caching."""

		# Merge schema provider_params with call-time kwargs (call-time takes precedence)
		provider_params = self._service_config.provider_params.copy()
		provider_params.update(kwargs)

		# Select model schema
		model_schema = self._service_config.main if model_type == "main" else self._service_config.weak

		# Instantiate using the stored class reference
		return self._service_config.model_class(
			model_name=model_schema.params.model,  # pyright: ignore[reportCallIssue]
			max_tokens=model_schema.constraints.max_output_tokens,  # pyright: ignore[reportCallIssue]
			api_key=self._service_config.api_key,  # pyright: ignore[reportCallIssue]
			**provider_params,
		)

	def get_main_model(self) -> BaseChatModel:
		"""Convenience method for accessing the primary model.

		Usage: `main_model = service.get_main_model()` -> high-capability model
		"""
		return self.get_model("main")

	def get_weak_model(self) -> BaseChatModel:
		"""Convenience method for accessing the secondary model.

		Usage: `weak_model = service.get_weak_model()` -> faster/cheaper model
		"""
		return self.get_model("weak")
