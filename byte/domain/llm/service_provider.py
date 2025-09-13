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
    """Service provider for LLM functionality."""

    def register(self, container: Container):
        """Register LLM services."""
        # Register the appropriate LLM service based on config/env
        llm_service = self._create_llm_service(container)
        container.singleton("llm_service", lambda: llm_service)

    def _create_llm_service(self, container):
        """Create the appropriate LLM service based on configuration."""
        # Check environment variable for preferred provider
        preferred_provider = os.getenv("BYTE_LLM_PROVIDER", "").lower()

        # Provider priority order
        providers = [
            ("anthropic", AnthropicLLMService),
            ("openai", OpenAILLMService),
            ("gemini", GeminiLLMService),
        ]

        # If preferred provider is specified and available, use it
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

        # Fall back to first available provider
        for name, service_class in providers:
            service = service_class(container)
            if service.is_available():
                return service

        raise RuntimeError("No LLM provider available. Please set API keys.")

    def boot(self, container: Container):
        """Boot LLM services."""
        llm_service: LLMService = container.make("llm_service")
        console: Console = container.make("console")

        # Get model configurations to display actual model names
        config = llm_service.get_model_config()
        main_model = config.get("main", {}).get("model", "Unknown")
        weak_model = config.get("weak", {}).get("model", "Unknown")

        console.print("│", style="text")
        console.print(f"├─ [success]Main model:[/success] [info]{main_model}[/info]")
        console.print(f"├─ [success]Weak model:[/success] [info]{weak_model}[/info]")
        console.print("│", style="text")

    def provides(self) -> list:
        return ["llm_service"]
