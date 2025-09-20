from rich.console import Console

from byte.container import Container
from byte.core.service_provider import ServiceProvider
from byte.domain.llm.service import LLMService


class LLMServiceProvider(ServiceProvider):
    """Service provider for LLM functionality.

    Automatically detects and configures the best available LLM provider
    based on environment variables and API key availability. Supports
    provider preference via BYTE_LLM_PROVIDER environment variable.
    Usage: Register with container to enable AI functionality throughout app
    """

    async def register(self, container: "Container") -> None:
        """Register LLM services with automatic provider selection.

        Usage: `provider.register(container)` -> configures best available LLM service
        """
        container.singleton(LLMService)

    async def boot(self, container: "Container") -> None:
        """Boot LLM services and display configuration information.

        Shows user which models are active for transparency and debugging,
        helping users understand which AI capabilities are available.
        Usage: Called automatically during application startup
        """
        llm_service = await container.make(LLMService)
        console = await container.make(Console)

        # Display active model configuration for user awareness
        main_model = llm_service._service_config.main.model
        weak_model = llm_service._service_config.weak.model
        console.print(f"├─ [success]Main model:[/success] [info]{main_model}[/info]")
        console.print(f"├─ [success]Weak model:[/success] [info]{weak_model}[/info]")

    def provides(self) -> list:
        """Return list of services provided by this provider."""
        return ["llm_service"]
