from typing import TYPE_CHECKING, Any

from byte.core.config.schema import Config

if TYPE_CHECKING:
    from byte.core.config.service import ConfigService


class Configurable:
    """Mixin that provides type-safe config access to services.

    Enables services to access configuration using self.config.app.name
    syntax, with automatic container resolution and type safety.
    Usage: `class MyService(Configurable): ...` then `self.config.app.name`
    """

    # Type hint for container attribute that will be provided by classes using this mixin
    container: Any
    _config_service: "ConfigService"

    def boot_configurable(self) -> None:
        """Boot method for Configurable mixin - automatically called by Command.__init__."""
        if hasattr(self, "container") and self.container:
            self._config_service = self.container.make("config")

    @property
    def config(self) -> Config:
        """Get strongly-typed configuration object.

        Usage: `self.config.app.name` -> type-safe access to configuration
        """
        if not hasattr(self, "_config_service"):
            # Return default config if service not available
            from pathlib import Path

            return Config.from_dict({}, Path.cwd(), False)

        return self._config_service.config
