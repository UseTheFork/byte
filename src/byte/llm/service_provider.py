from __future__ import annotations

from byte import EventBus, Events, ServiceProvider
from byte.llm import LLMService


class LLMServiceProvider(ServiceProvider):
    """Service provider for LLM functionality.

    Automatically detects and configures the best available LLM provider
    based on environment variables and API key availability. Supports
    provider preference via BYTE_LLM_PROVIDER environment variable.
    Usage: Register with container to enable AI functionality throughout app
    """

    async def boot(self) -> None:
        """Boot LLM services and display configuration information.

        Shows user which models are active for transparency and debugging,
        helping users understand which AI capabilities are available.
        Usage: Called automatically during application startup
        """
        event_bus = self.app.make(EventBus)
        llm_service = self.app.make(LLMService)

        # Register listener that calls list_in_context_files before each prompt
        event_bus.on(
            Events.GatherReinforcement,
            llm_service.add_reinforcement_hook,
        )

        event_bus.on(
            Events.PostBoot,
            self.boot_messages,
        )

    async def boot_messages(self, payload: Events.PostBoot) -> Events.PostBoot:
        llm_service = self.app.make(LLMService)
        # Display active model configuration for user awareness
        reasoning_model = f"{llm_service._reasoning_schema.provider}:{llm_service._reasoning_schema.model}"
        main_model = f"{llm_service._main_schema.provider}:{llm_service._main_schema.model}"
        weak_model = f"{llm_service._weak_schema.provider}:{llm_service._weak_schema.model}"

        payload.messages.append(f"[$text-muted]Reasoning model:[/$text-muted] [$primary]{reasoning_model}[/$primary]")
        payload.messages.append(f"[$text-muted]Main model:[/$text-muted] [$primary]{main_model}[/$primary]")
        payload.messages.append(f"[$text-muted]Weak model:[/$text-muted] [$primary]{weak_model}[/$primary]")

        return payload
