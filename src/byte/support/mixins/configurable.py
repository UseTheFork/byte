from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from byte.config import ByteConfig
    from byte.foundation import Application


class Configurable:
    app: Application

    def _configure_service(self) -> None:
        """Override this method to set service-specific configuration."""
        pass

    def boot_configurable(self, **kwargs) -> None:
        self._config: ByteConfig = self.app.make("config")
        self._service_config = {}
        self._configure_service()
