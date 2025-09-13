from typing import TYPE_CHECKING

from rich.console import Console

from byte.core.config.service import ConfigService
from byte.core.service_provider import ServiceProvider

if TYPE_CHECKING:
    from byte.container import Container


class ConfigServiceProvider(ServiceProvider):
    """Service provider for configuration management.

    Registers ConfigService with automatic workspace initialization,
    creating .byte directory and default config.yaml as needed.
    Usage: Register with container to enable config('app.name') access
    """

    def register(self, container: "Container") -> None:
        """Register configuration services in the container."""
        # ConfigService automatically initializes workspace and loads config.yaml
        # TODO: Pass CLI args when available
        container.singleton("config", lambda: ConfigService())

    def boot(self, container: "Container") -> None:
        """Boot configuration services after all providers are registered."""
        console: Console = container.make("console")
        config_service = container.make("config")

        console.print("│", style="text")
        console.print(
            f"├─ [success]Project root:[/success] [info]{config_service.project_root}[/info]"
        )
        console.print("│", style="text")

    def provides(self) -> list:
        """Return list of services provided by this provider."""
        return ["config"]
