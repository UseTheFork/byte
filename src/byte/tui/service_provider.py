from byte import EventBus, Events
from byte.support import ServiceProvider
from byte.tui import TUIManagerService


class TUIServiceProvider(ServiceProvider):
    """Service provider for UI system."""

    def services(self):
        return [
            TUIManagerService,
        ]

    async def boot(self):
        """Boot UI services."""
        event_bus = self.app.make(EventBus)
        tui_manager_service = self.app.make(TUIManagerService)

        event_bus.on(
            Events.TuiMessage,
            tui_manager_service.route_message,
        )
        event_bus.on(
            Events.UserInputSubmitted,
            tui_manager_service.handle_user_message,
        )
