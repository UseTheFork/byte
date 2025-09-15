from rich.console import Console

from byte.container import Container
from byte.core.config.service import ConfigService
from byte.core.service_provider import ServiceProvider
from byte.domain.llm.config import LLMConfig, ModelConfig
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
        container.bind("llm_service", lambda: LLMService(container))

    async def configure(self, container: "Container") -> None:
        """Configure lint domain settings after registration but before boot.

        Handles lint-specific configuration parsing, validation, and storage.
        Usage: Called automatically during container configure phase
        """
        # Get the config service to access raw configuration data
        config_service: ConfigService = await container.make("config")

        # Get raw config data from all sources
        yaml_config, env_config, cli_config = config_service.get_raw_config()

        model = yaml_config.get("model", "")

        if model == "sonnet":
            main_model = ModelConfig(model="claude-sonnet-4-20250514")
            weak_model = ModelConfig(model="claude-3-5-haiku-20241022")

        llm_config = LLMConfig(base=model, main=main_model, weak=weak_model)

        llm_service: LLMService = await container.make("llm_service")
        llm_service.set_config(llm_config)

    async def boot(self, container: "Container") -> None:
        """Boot LLM services and display configuration information.

        Shows user which models are active for transparency and debugging,
        helping users understand which AI capabilities are available.
        Usage: Called automatically during application startup
        """
        llm_service: LLMService = await container.make("llm_service")
        console: Console = await container.make("console")

        # Display active model configuration for user awareness
        main_model = llm_service._config.main.model
        weak_model = llm_service._config.weak.model

        console.print("│", style="text")
        console.print(f"├─ [success]Main model:[/success] [info]{main_model}[/info]")
        console.print(f"├─ [success]Weak model:[/success] [info]{weak_model}[/info]")
        console.print("│", style="text")

    def provides(self) -> list:
        """Return list of services provided by this provider."""
        return ["llm_service"]
