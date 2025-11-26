from typing import TYPE_CHECKING, Optional

from byte.core.config.config import ByteConfg

if TYPE_CHECKING:
    from byte.container import Container


class Configurable:
    container: Optional["Container"]

    async def boot_configurable(self, **kwargs) -> None:
        self._config: ByteConfg = await self.container.make(ByteConfg)  # pyright: ignore[reportOptionalMemberAccess]
        self._service_config = {}
        await self._configure_service()

    async def _configure_service(self) -> None:
        """Override this method to set service-specific configuration."""
        pass
