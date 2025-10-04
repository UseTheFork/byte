from typing import Any, Dict

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel

from byte.core.service.base_service import Service
from byte.domain.llm.config import LLMConfig, ModelConfig


class LLMService(Service):
    """Base LLM service that all providers extend.

    Provides a unified interface for different LLM providers (OpenAI, Anthropic, etc.)
    with model caching and configuration management. Enables provider-agnostic
    AI functionality throughout the application.
    Usage: `service = OpenAILLMService(container)` -> provider-specific implementation
    """

    _models: Dict[str, Any] = {}
    _service_config: LLMConfig

    async def _configure_service(self) -> None:
        """Configure LLM service with model settings based on global configuration."""
        if self._config.model == "sonnet":
            main_model = ModelConfig(
                model="claude-sonnet-4-5",
                max_input_tokens=200000,
                max_output_tokens=64000,
                input_cost_per_token=(3 / 1000000),
                output_cost_per_token=(15 / 1000000),
            )
            weak_model = ModelConfig(
                model="claude-3-5-haiku-latest",
                max_input_tokens=200000,
                max_output_tokens=8192,
                input_cost_per_token=(0.80 / 1000000),
                output_cost_per_token=(4 / 1000000),
            )

        self._service_config = LLMConfig(
            model=self._config.model, main=main_model, weak=weak_model
        )

    def get_model(self, model_type: str = "main", **kwargs) -> Any:
        """Get a model instance with lazy initialization and caching.

        Retrieves cached model or creates new one based on configuration,
        reducing initialization overhead for frequently used models.
        Usage: `model = service.get_model("main")` -> cached LangChain model instance
        """

        # TODO: Need to figure out how to make this handle for other providers.

        if model_type == "main":
            return ChatAnthropic(
                model_name=self._service_config.main.model,
                max_tokens=self._service_config.main.max_output_tokens,
                **kwargs,
            )
        elif model_type == "weak":
            return ChatAnthropic(
                model_name=self._service_config.weak.model,
                max_tokens=self._service_config.weak.max_output_tokens,
                **kwargs,
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
