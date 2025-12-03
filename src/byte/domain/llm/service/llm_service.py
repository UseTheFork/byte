from typing import Any

from langchain_core.language_models import BaseChatModel

from byte.core.event_bus import Payload
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

        params_dict = model_schema.params.model_dump(exclude_none=True)

        # Instantiate using the stored class reference
        return self._service_config.model_class(
            max_tokens=model_schema.constraints.max_output_tokens,  # pyright: ignore[reportCallIssue]
            api_key=self._service_config.api_key,  # pyright: ignore[reportCallIssue]
            **params_dict,
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

    async def add_reinforcement_hook(self, payload: Payload) -> Payload:
        """Add reinforcement messages based on model's reinforcement mode.

        Checks the reinforcement mode of the model being used and adds
        appropriate reinforcement messages if configured.

        Usage: `payload = await service.add_reinforcement_hook(payload)`
        """
        # TODO: should we also check what agent this is?
        mode = payload.get("mode", "main")

        # Select model schema based on mode
        model_schema = self._service_config.main if mode == "main" else self._service_config.weak

        reinforcement = []

        # Check reinforcement mode and add messages accordingly
        if model_schema.behavior.reinforcement_mode.value == "eager":
            # Add strong reinforcement for eager mode
            reinforcement.extend(
                [
                    "IMPORTANT: Pay careful attention to the scope of the user's request."
                    "- DO what they ask, but no more."
                    "- DO NOT improve, comment, fix or modify unrelated parts of the code in any way!",
                ]
            )

        elif model_schema.behavior.reinforcement_mode.value == "lazy":
            # Add gentle reinforcement for lazy mode
            reinforcement.extend(
                [
                    "IMPORTANT: You are diligent and tireless!"
                    "- You NEVER leave comments describing code without implementing it!"
                    "- You always COMPLETELY IMPLEMENT the needed code!",
                ]
            )

        # Get existing list and extend with reinforcement messages
        reinforcement_list = payload.get("reinforcement", [])
        reinforcement_list.extend(reinforcement)
        payload.set("reinforcement", reinforcement_list)

        return payload
