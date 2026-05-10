from __future__ import annotations

from byte import EventBus, ServiceProvider
from byte.llm import LLMService
from byte.orchestration import OrchestrationEvents


class LLMServiceProvider(ServiceProvider):
    """Service provider for LLM functionality.

    Automatically detects and configures the best available LLM provider
    based on environment variables and API key availability. Supports
    provider preference via BYTE_LLM_PROVIDER environment variable.
    Usage: Register with container to enable AI functionality throughout app
    """

    async def boot(self):
        """Boot LLM services and display configuration information.

        Shows user which models are active for transparency and debugging,
        helping users understand which AI capabilities are available.
        Usage: Called automatically during application startup
        """
        event_bus = self.app.make(EventBus)
        llm_service = self.app.make(LLMService)

        # Register listener that calls list_in_context_files before each prompt
        event_bus.on(
            OrchestrationEvents.GatherReinforcement,
            llm_service.add_reinforcement_hook,
        )
