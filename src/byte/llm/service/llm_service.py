from typing import Any

from langchain.chat_models import BaseChatModel, init_chat_model

from byte import Payload, Service
from byte.foundation.exceptions import ByteConfigException
from byte.llm import (
    ModelBehavior,
    ModelConstraints,
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

        extra_params = {"temperature": 0.1}

        if model_type == "weak":
            config_params = self.app["config"].llm.main_model.extra_params
        else:
            config_params = self.app["config"].llm.weak_model.extra_params

        combined_params = {**extra_params, **config_params}

        # Add provider-specific params
        if provider == "openai":
            combined_params["stream_usage"] = True

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

        return ModelSchema(
            provider=provider,
            model=model_id,
            constraints=constraints,
            behavior=behavior,
            extra_params=combined_params,
        )

    def boot(self) -> None:
        """Configure LLM service with model settings based on global configuration."""

        # Load models data from YAML
        models_data_path = self.app.app_path("llm/resources/models_data.yaml")
        self.models_data = Yaml.load_as_dict(models_data_path)

        # Get configured models
        main_model_id = self.app["config"].llm.main_model.model
        weak_model_id = self.app["config"].llm.weak_model.model

        # Verify main_model exists in models_data
        if main_model_id not in self.models_data:
            raise ByteConfigException(f"Main model '{main_model_id}' not found in models_data.yaml")

        # Verify weak_model exists in models_data
        if weak_model_id not in self.models_data:
            raise ByteConfigException(f"Weak model '{weak_model_id}' not found in models_data.yaml")

        # Configure model schemas
        self._main_schema = self._configure_model_schema(main_model_id, "main")
        self._weak_schema = self._configure_model_schema(weak_model_id, "weak")

    def get_model(self, model_type: str = "main", **kwargs) -> Any:
        """Get a model instance with lazy initialization and caching."""

        # Select model schema
        model_schema = self._main_schema if model_type == "main" else self._weak_schema
        params_dict = model_schema.extra_params

        # Merge all parameters, with later dictionaries taking precedence
        merged_params = {
            **params_dict,
            **kwargs,
        }

        compiled_agent = init_chat_model(f"{model_schema.provider}:{model_schema.model}", **merged_params)
        return compiled_agent

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
                    "IMPORTANT: Pay careful attention to the scope of the user's request.",
                    "- DO what they ask, but no more.",
                    "- DO NOT improve, comment, fix or modify unrelated parts of the code in any way!",
                ]
            )

        elif model_schema.behavior.reinforcement_mode.value == "lazy":
            # Add gentle reinforcement for lazy mode
            reinforcement.extend(
                [
                    "IMPORTANT: You are diligent and tireless!",
                    "- You NEVER leave comments describing code without implementing it!",
                    "- You always COMPLETELY IMPLEMENT the needed code!",
                ]
            )

        # Get existing list and extend with reinforcement messages
        reinforcement_list = payload.get("reinforcement", [])
        reinforcement_list.extend(reinforcement)
        payload.set("reinforcement", reinforcement_list)

        return payload
