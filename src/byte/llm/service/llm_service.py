from typing import Any, Type

from langchain.chat_models import BaseChatModel
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from byte import Payload, Service
from byte.foundation.exceptions import ByteConfigException
from byte.llm import (
    ModelBehavior,
    ModelConstraints,
    ModelParams,
    ModelProvider,
    ModelSchema,
    ReinforcementMode,
)
from byte.support import Yaml


class LLMService(Service):
    """Base LLM service that all providers extend.

    Provides a unified interface for different LLM providers (OpenAI, Anthropic, etc.)
    with model caching and configuration management. Enables provider-agnostic
    AI functionality throughout the application.
    Usage: `service = LLMService(app)` -> provider-specific implementation
    """

    def _get_default_model_for_provider(self, provider: str, model_type: str = "main") -> str:
        """Get default model ID for a specific provider.

        Args:
            provider: Provider name ("anthropic", "openai", "google")
            model_type: Either "main" or "weak"

        Returns:
            Default model ID for the provider

        Raises:
            ByteConfigException: If provider is not recognized
        """
        defaults = {
            "anthropic": ("claude-sonnet-4-5", "claude-3-5-haiku-latest"),
            "openai": ("gpt-5", "gpt-5-mini"),
            "google": ("gemini-2.5-pro", "gemini-2.5-flash-lite"),
        }

        if provider not in defaults:
            raise ByteConfigException(f"Unknown provider: {provider}")

        return defaults[provider][0] if model_type == "main" else defaults[provider][1]

    def _get_default_models(self) -> tuple[str, str]:
        """Get default main and weak model IDs based on enabled providers.

        Returns:
            Tuple of (main_model_id, weak_model_id)

        Raises:
            ByteConfigException: If no providers are enabled
        """
        if self.app["config"].llm.providers.anthropic.enable:
            return ("claude-sonnet-4-5", "claude-3-5-haiku-latest")
        elif self.app["config"].llm.providers.gemini.enable:
            return ("gemini-2.5-pro", "gemini-2.5-flash-lite")
        elif self.app["config"].llm.providers.openai.enable:
            return ("gpt-5", "gpt-5-mini")
        else:
            raise ByteConfigException("No LLM providers are enabled. Please enable at least one provider.")

    def _get_extra_params(self, provider: str, model_type: str) -> dict[str, Any]:
        """Get combined extra_params from model config and provider config.

        Args:
            provider: Provider name ("anthropic", "openai", "google")
            model_type: Either "main" or "weak"

        Returns:
            Combined dictionary of extra parameters
        """
        # Get model-specific extra_params
        model_config = self.app["config"].llm.main_model if model_type == "main" else self.app["config"].llm.weak_model
        model_extra_params = model_config.extra_params or {}

        # Get provider-specific extra_params
        provider_config_map = {
            "anthropic": self.app["config"].llm.providers.anthropic,
            "openai": self.app["config"].llm.providers.openai,
            "google": self.app["config"].llm.providers.gemini,
        }
        provider_config = provider_config_map.get(provider)
        provider_extra_params = provider_config.extra_params if provider_config else {}

        # Combine both dictionaries (provider params take precedence)
        combined_params = {
            **provider_extra_params,
            **model_extra_params,
        }

        return combined_params

    def _configure_model_schema(self, model_id: str, model_type: str) -> ModelSchema:
        """Configure a ModelSchema from models_data.yaml.

        Args:
            model_id: The model identifier (e.g., "claude-sonnet-4-5")
            model_type: Either "main" or "weak"

        Returns:
            Configured ModelSchema instance

        Raises:
            ByteConfigException: If model not found in models_data
        """
        if model_id not in self.models_data:
            raise ByteConfigException(f"Model '{model_id}' not found in models_data.yaml")

        model_data = self.models_data[model_id]
        provider = model_data["provider"]

        # Map provider to model class
        provider_class_map: dict[str, Type[BaseChatModel]] = {
            "anthropic": ChatAnthropic,
            "openai": ChatOpenAI,
            "google": ChatGoogleGenerativeAI,
        }
        model_class = provider_class_map.get(provider)

        # Build ModelParams
        params = ModelParams(
            model=model_id,
            temperature=0.1,
        )

        # Add provider-specific params
        if provider == "openai":
            params.stream_usage = True

        # Build ModelConstraints from YAML data
        constraints = ModelConstraints(
            max_input_tokens=model_data["limit"]["context"],
            max_output_tokens=model_data["limit"]["output"],
            input_cost_per_token=model_data["cost"]["input"],
            output_cost_per_token=model_data["cost"]["output"],
            input_cost_per_token_cached=model_data["cost"]["cache_read"],
        )

        # Build ModelBehavior with provider and type-specific settings
        reinforcement_mode = ReinforcementMode.NONE
        if provider == "anthropic" and model_type == "main":
            reinforcement_mode = ReinforcementMode.EAGER

        behavior = ModelBehavior(reinforcement_mode=reinforcement_mode)

        # Get provider config from app config
        provider_config_map = {
            "anthropic": self.app["config"].llm.providers.anthropic,
            "openai": self.app["config"].llm.providers.openai,
            "google": self.app["config"].llm.providers.gemini,
        }
        app_provider_config = provider_config_map.get(provider)

        model_provider = ModelProvider(
            api_key=app_provider_config.api_key,
        )

        # Get combined extra_params
        extra_params = self._get_extra_params(provider, model_type)

        return ModelSchema(
            model_class=model_class,
            params=params,
            constraints=constraints,
            behavior=behavior,
            provider=model_provider,
            extra_params=extra_params,
        )

    def boot(self) -> None:
        """Configure LLM service with model settings based on global configuration."""

        # Load models data from YAML
        models_data_path = self.app.app_path("llm/resources/models_data.yaml")
        self.models_data = Yaml.load_as_dict(models_data_path)

        # Get configured models
        main_model_id = self.app["config"].llm.main_model.model
        weak_model_id = self.app["config"].llm.weak_model.model

        # Use provider-specific defaults if models are not set or if they match provider names
        if not main_model_id or main_model_id in ("anthropic", "openai", "google"):
            if main_model_id in ("anthropic", "openai", "google"):
                main_model_id = self._get_default_model_for_provider(main_model_id, "main")
            else:
                default_main, _ = self._get_default_models()
                main_model_id = default_main

        if not weak_model_id or weak_model_id in ("anthropic", "openai", "google"):
            if weak_model_id in ("anthropic", "openai", "google"):
                weak_model_id = self._get_default_model_for_provider(weak_model_id, "weak")
            else:
                _, default_weak = self._get_default_models()
                weak_model_id = default_weak

        # Verify main_model exists in models_data
        if main_model_id not in self.models_data:
            raise ByteConfigException(f"Main model '{main_model_id}' not found in models_data.yaml")

        # Verify weak_model exists in models_data
        if weak_model_id not in self.models_data:
            raise ByteConfigException(f"Weak model '{weak_model_id}' not found in models_data.yaml")

        # Get provider for main_model
        main_model_provider = self.models_data[main_model_id]["provider"]

        # Get provider for weak_model
        weak_model_provider = self.models_data[weak_model_id]["provider"]

        # Check if main_model provider is enabled
        if main_model_provider == "anthropic":
            if not self.app["config"].llm.providers.anthropic.enable:
                raise ByteConfigException(f"Main model '{main_model_id}' requires Anthropic provider to be enabled")
        elif main_model_provider == "openai":
            if not self.app["config"].llm.providers.openai.enable:
                raise ByteConfigException(f"Main model '{main_model_id}' requires OpenAI provider to be enabled")
        elif main_model_provider == "google":
            if not self.app["config"].llm.providers.gemini.enable:
                raise ByteConfigException(f"Main model '{main_model_id}' requires Gemini provider to be enabled")

        # Check if weak_model provider is enabled
        if weak_model_provider == "anthropic":
            if not self.app["config"].llm.providers.anthropic.enable:
                raise ByteConfigException(f"Weak model '{weak_model_id}' requires Anthropic provider to be enabled")
        elif weak_model_provider == "openai":
            if not self.app["config"].llm.providers.openai.enable:
                raise ByteConfigException(f"Weak model '{weak_model_id}' requires OpenAI provider to be enabled")
        elif weak_model_provider == "google":
            if not self.app["config"].llm.providers.gemini.enable:
                raise ByteConfigException(f"Weak model '{weak_model_id}' requires Gemini provider to be enabled")

        # Configure model schemas
        self._main_schema = self._configure_model_schema(main_model_id, "main")
        self._weak_schema = self._configure_model_schema(weak_model_id, "weak")

    def get_model(self, model_type: str = "main", **kwargs) -> Any:
        """Get a model instance with lazy initialization and caching."""

        # Select model schema
        model_schema = self._main_schema if model_type == "main" else self._weak_schema

        schema_params = model_schema.params.model_dump(exclude_none=True)
        provider_params_dict = model_schema.provider.params
        params_dict = model_schema.extra_params

        # Merge all parameters, with later dictionaries taking precedence
        merged_params = {
            **schema_params,
            **provider_params_dict,
            **params_dict,
            **kwargs,
        }

        # Instantiate using the stored class reference
        return model_schema.model_class(
            max_tokens=model_schema.constraints.max_output_tokens,
            api_key=model_schema.provider.api_key,
            **merged_params,
        )  # ty:ignore[call-non-callable]

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
        model_schema = self._main_schema if mode == "main" else self._weak_schema

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
