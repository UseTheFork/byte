from __future__ import annotations

from byte import EventBus, ServiceProvider
from byte.foundation import TaskManager
from byte.tui import ByteTUI


class FoundationServiceProvider(ServiceProvider):
    """ """

    def register(self) -> None:
        """ """

        self.app.singleton(ByteTUI)

        self.app.singleton(EventBus)

        self.app.singleton(TaskManager)
        self.app.make(TaskManager)
