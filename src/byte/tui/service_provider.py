from byte import EventBus
from byte.support import ServiceProvider
from byte.tui import TuiEvents, TUIManagerService


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
            TuiEvents.ComponentEvent,
            tui_manager_service.route_event,
        )
        event_bus.on(
            TuiEvents.UserInputSubmitted,
            tui_manager_service.handle_user_message,
        )
