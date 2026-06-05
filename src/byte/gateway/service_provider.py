import asyncio
from typing import TYPE_CHECKING

from byte.gateway.config import GatewayConfig
from byte.gateway.service.gateway_service import GatewayService
from byte.support import ServiceProvider

if TYPE_CHECKING:
    from byte.foundation import Application


class GatewayServiceProvider(ServiceProvider):
    """Register and boot the gateway WebSocket server."""

    def register(self) -> None:
        """Bind GatewayService as a singleton in the container."""
        self.app.singleton(GatewayService)

    async def boot(self) -> None:
        """Start the gateway server in a background task if gateway.enable is True."""
        config: GatewayConfig = self.app["config"].gateway
        if not config.enable:
            return

        # TODO: This should use the task service.

        gateway: GatewayService = self.app.make(GatewayService)
        asyncio.get_event_loop().create_task(gateway.start())

    async def shutdown(self, app: Application) -> None:
        """Stop the gateway server on application shutdown."""
        config: GatewayConfig = app["config"].gateway
        if not config.enable:
            return

        gateway: GatewayService = app.make(GatewayService)
        await gateway.stop()
