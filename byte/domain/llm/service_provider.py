import os
from typing import TYPE_CHECKING

from rich.console import Console

from byte.container import Container
from byte.core.service_provider import ServiceProvider
from byte.domain.llm.providers.anthropic import AnthropicLLMService
from byte.domain.llm.providers.gemini import GeminiLLMService
from byte.domain.llm.providers.openai import OpenAILLMService

if TYPE_CHECKING:
    from byte.domain.llm.service import LLMService


class LLMServiceProvider(ServiceProvider):
    """Service provider for LLM functionality.

    Automatically detects and configures the best available LLM provider
    based on environment variables and API key availability. Supports
    provider preference via BYTE_LLM_PROVIDER environment variable.
    Usage: Register with container to enable AI functionality throughout app
    """

    def register(self, container: "Container") -> None:
        """Register LLM services with automatic provider selection.

        Usage: `provider.register(container)` -> configures best available LLM service
        """
        llm_service = self._create_llm_service(container)
        container.singleton("llm_service", lambda: llm_service)

    def _create_llm_service(self, container: "Container") -> "LLMService":
        """Create the appropriate LLM service based on configuration.

        Respects user preference from environment variable, falling back
        to first available provider if preferred option is unavailable.
        Usage: Called internally during service registration
        """
        preferred_provider = os.getenv("BYTE_LLM_PROVIDER", "").lower()

        # Provider priority order - Anthropic first for best performance
        providers = [
            ("anthropic", AnthropicLLMService),
            ("openai", OpenAILLMService),
            ("gemini", GeminiLLMService),
        ]

        # Honor user preference if specified and available
        if preferred_provider:
            for name, service_class in providers:
                if name == preferred_provider:
                    service = service_class(container)
                    if service.is_available():
                        return service
                    else:
                        print(
                            f"Warning: Preferred provider '{preferred_provider}' not available"
                        )
                        break

        # Fall back to first available provider for seamless experience
        for name, service_class in providers:
            service = service_class(container)
            if service.is_available():
                return service

        raise RuntimeError("No LLM provider available. Please set API keys.")

    def boot(self, container: "Container") -> None:
        """Boot LLM services and display configuration information.

        Shows user which models are active for transparency and debugging,
        helping users understand which AI capabilities are available.
        Usage: Called automatically during application startup
        """
        llm_service: LLMService = container.make("llm_service")
        console: Console = container.make("console")

        # Display active model configuration for user awareness
        config = llm_service.get_model_config()
        main_model = config.get("main", {}).get("model", "Unknown")
        weak_model = config.get("weak", {}).get("model", "Unknown")

        console.print("│", style="text")
        console.print(f"├─ [success]Main model:[/success] [info]{main_model}[/info]")
        console.print(f"├─ [success]Weak model:[/success] [info]{weak_model}[/info]")
        console.print("│", style="text")

    def provides(self) -> list:
        """Return list of services provided by this provider."""
        return ["llm_service"]
