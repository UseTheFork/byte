from byte.support import ServiceProvider
from byte.tui import TUIManagerService


class TUIServiceProvider(ServiceProvider):
    """Service provider for UI system."""

    def services(self):
        return [
            TUIManagerService,
        ]

    # async def boot(self):
    #     """Boot UI services."""
    #     event_bus = self.app.make(EventBus)

    #     event_bus.on(
    #         EventType.POST_BOOT.value,
    #         self.boot_messages,
    #     )
