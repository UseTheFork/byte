---
files:
  create:
  - src/byte/gateway/provider.py
  edit: []
  reference:
  - src/byte/support/service_provider.py
  - src/byte/git/service_provider.py
  - src/byte/gateway/service/gateway_service.py
  - src/byte/gateway/config.py
id: create-gateway-provider
notes: []
order: 6
status: completed
---
# Gateway Domain — `provider.py`
**Goal:** Wire `GatewayService` into the dependency injection container and conditionally schedule its async start without blocking the TUI event loop.
**Architecture:** `GatewayServiceProvider` follows the same pattern as `GitServiceProvider` — extend `ServiceProvider`, implement `register` and `boot`. The provider is the only place that checks `gateway.enable`; all other gateway code assumes it is always running.

---

## Create `src/byte/gateway/provider.py`

```python
import asyncio

from byte.gateway.config import GatewayConfig
from byte.gateway.service.gateway_service import GatewayService
from byte.support import ServiceProvider


class GatewayServiceProvider(ServiceProvider):
    """Register and boot the gateway WebSocket server."""

    def register(self) -> None:
        """Bind GatewayService as a singleton in the container."""
        self.app.singleton(
            GatewayService,
            lambda app: GatewayService(app, app["config"].gateway),
        )

    async def boot(self) -> None:
        """Start the gateway server in a background task if gateway.enable is True."""
        config: GatewayConfig = self.app["config"].gateway
        if not config.enable:
            return

        gateway: GatewayService = self.app.make(GatewayService)
        asyncio.get_event_loop().create_task(gateway.start())

    async def shutdown(self, app) -> None:
        """Stop the gateway server on application shutdown."""
        config: GatewayConfig = app["config"].gateway
        if not config.enable:
            return

        gateway: GatewayService = app.make(GatewayService)
        await gateway.stop()
```

> **Note on `boot` signature**: `ServiceProvider.boot` is `async def` in `service_provider.py` — keep it async here to match.
