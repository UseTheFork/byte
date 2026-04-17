from byte import EventBus
from byte.support import ServiceProvider
from byte.tui import PromptHistoryService, TuiEvents, TUIManagerService


class TUIServiceProvider(ServiceProvider):
    """Service provider for UI system."""

    def services(self):
        return [
            TUIManagerService,
            PromptHistoryService,
        ]

    async def boot(self):
        """Boot UI services."""
        event_bus = self.app.make(EventBus)
        tui_manager_service = self.app.make(TUIManagerService)
        prompt_history_service = self.app.make(PromptHistoryService)
        self.app.dispatch_task(prompt_history_service.load())

        # event_bus.on(
        #     FileEvents.FileStats,
        #     tui_manager_service.on_file_events_file_stats,
        # )

        event_bus.on(
            TuiEvents.UserInputSubmitted,
            tui_manager_service.handle_user_message,
        )
        # event_bus.on(
        #     TuiEvents.PromptUser,
        #     tui_manager_service.handle_prompt_user,
        # )
