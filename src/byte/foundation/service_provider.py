from byte import EventBus, ServiceProvider
from byte.foundation import TaskManager
from byte.node import NodeRegistry
from byte.tui import ByteTUI


class FoundationServiceProvider(ServiceProvider):
    """Service provider for core foundation services including TUI, event bus, and task management."""

    def register(self) -> None:
        """Register core foundation singletons into the application container."""

        self.app.singleton(ByteTUI)

        self.app.singleton(NodeRegistry)

        self.app.singleton(EventBus)

        self.app.singleton(TaskManager)
        self.app.make(TaskManager)
