from typing import cast

from langchain.chat_models import BaseChatModel
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_openrouter import ChatOpenRouter

from byte import Service
from byte.llm import LLMRegistryService, ModelSchema
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

    def init_chat_model(self, model_schema: ModelSchema, **kwargs) -> BaseChatModel:

        # temperature=0,
        # max_tokens=1024,
        # max_retries=2,
        # other params...

        merged_params = {
            "temperature": 0.1,
            **model_schema.extra_params,
            **kwargs,
        }

        if model_schema.provider == "openrouter":
            return ChatOpenRouter(
                model=model_schema.model,
                **merged_params,  # ty:ignore[invalid-argument-type]
            )
        elif model_schema.provider == "anthropic":
            return ChatAnthropic(
                model=model_schema.model,
                **merged_params,  # ty:ignore[invalid-argument-type]
            )
        elif model_schema.provider == "openai":
            return ChatOpenAI(
                model=model_schema.model,
                **merged_params,  # ty:ignore[invalid-argument-type]
            )
        else:
            return ChatGoogleGenerativeAI(
                model=model_schema.model,
                **merged_params,
            )

    def get_model(self, agent_id: str, **kwargs) -> ModelSchema:
        """Get a model schema and merged parameters for initialization.

        Returns a tuple of (model_schema, merged_params) instead of a compiled model,
        allowing callers to customize initialization as needed.

        Args:
            model_id: The configuration key (e.g., "ask", "coder", "commit")
            **kwargs: Additional parameters to merge with model configuration

        Returns:
            Tuple of (ModelSchema, dict) containing model configuration and merged parameters
        """

        # Use getattr to dynamically access the config attribute
        model_config = getattr(self.app["config"].llm, agent_id, None)
        if model_config is None:
            raise ValueError(f"Model configuration not found for: {agent_id}")

        model_id_from_config = model_config.model

        model_schema = cast(ModelSchema, self.llm_registry.get_model(str(model_config.provider), model_id_from_config))
        model_schema.provider = str(model_config.provider)
        model_schema.extra_params = model_config.extra_params

        return model_schema

    async def add_reinforcement_hook(
        self, payload: OrchestrationEvents.GatherReinforcement
    ) -> OrchestrationEvents.GatherReinforcement:
        """Add reinforcement messages based on model's reinforcement mode.

        Checks the reinforcement mode of the model being used and adds
        appropriate reinforcement messages if configured.

        Usage: `payload = await service.add_reinforcement_hook(payload)`
        """

        reinforcement = []

        # Check reinforcement mode and add messages accordingly
        if payload.provider in ["anthropic", "openai"]:
            # Add strong reinforcement for eager mode
            reinforcement.extend(
                [
                    "IMPORTANT: Pay careful attention to the scope of the user's request.",
                    "- DO what they ask, but no more.",
                    "- DO NOT improve, comment, fix or modify unrelated parts of the code in any way!",
                ]
            )

        elif payload.provider == "google":
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
