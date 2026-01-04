from typing import TYPE_CHECKING, Optional

from byte.core import ByteConfig

if TYPE_CHECKING:
    from byte.container import Container


class Configurable:
    container: Optional["Container"]

    async def _configure_service(self) -> None:
        """Override this method to set service-specific configuration."""
        pass

    async def boot_configurable(self, **kwargs) -> None:
        self._config: ByteConfig = await self.container.make(ByteConfig)  # pyright: ignore[reportOptionalMemberAccess]
        self._service_config = {}
        await self._configure_service()
