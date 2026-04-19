from langchain.chat_models import BaseChatModel, init_chat_model

from byte import Service
from byte.llm import LLMRegistryService
from byte.orchestration import OrchestrationEvents


class LLMService(Service):
    """Base LLM service that all providers extend.

    Provides a unified interface for different LLM providers (OpenAI, Anthropic, etc.)
    with model caching and configuration management. Enables provider-agnostic
    AI functionality throughout the application.
    Usage: `service = LLMService(app)` -> provider-specific implementation
    """

    def boot(self) -> None:
        """Configure LLM service with model settings based on global configuration."""
        self.llm_registry = self.app.make(LLMRegistryService)

    def get_model(self, model_id: str, **kwargs) -> BaseChatModel:
        """Get a model instance with lazy initialization and caching."""

        # Use getattr to dynamically access the config attribute
        model_config = getattr(self.app["config"].llm, model_id, None)
        if model_config is None:
            raise ValueError(f"Model configuration not found for: {model_id}")

        model_id_from_config = model_config.model

        model_schema = self.llm_registry.get_model(model_id_from_config)
        if model_schema is None:
            raise ValueError(f"Unknown configuration: {model_id}")

        params_dict = model_schema.extra_params

        # Merge all parameters, with later dictionaries taking precedence
        merged_params = {
            **params_dict,
            **kwargs,
        }

        compiled_agent = init_chat_model(f"{model_schema.provider}:{model_schema.model}", **merged_params)
        return compiled_agent

    async def add_reinforcement_hook(
        self, payload: OrchestrationEvents.GatherReinforcement
    ) -> OrchestrationEvents.GatherReinforcement:
        """Add reinforcement messages based on model's reinforcement mode.

        Checks the reinforcement mode of the model being used and adds
        appropriate reinforcement messages if configured.

        Usage: `payload = await service.add_reinforcement_hook(payload)`
        """
        pass
        # TODO: should we also check what agent this is?
        mode = payload.mode

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
        payload.reinforcement.extend(reinforcement)

        return payload
