from typing import TYPE_CHECKING

from byte.core.config.schema import BaseConfig

if TYPE_CHECKING:
    pass


class Configurable:
    def set_config(self, config: BaseConfig) -> None:
        """Set the configuration object directly.

        Usage: `service.set_config(domain_config)` -> sets config during configure phase
        """
        self._config = config

    @property
    def config(self) -> BaseConfig:
        """Get the service's configuration object.

        Usage: `self.config.enabled` -> access config properties
        """
        if not hasattr(self, "_config"):
            raise RuntimeError("Configuration not set. Call set_config() first.")
        return self._config
