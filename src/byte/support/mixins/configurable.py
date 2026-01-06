from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from byte.config import ByteConfig
    from byte.foundation import Application


class Configurable:
    app: Application

    async def _configure_service(self) -> None:
        """Override this method to set service-specific configuration."""
        pass

    async def boot_configurable(self, **kwargs) -> None:
        self._config: ByteConfig = await self.app.make("config")
        self._service_config = {}
        await self._configure_service()
