from __future__ import annotations

from byte import ServiceProvider
from byte.foundation import Console, EventBus, TaskManager


class FoundationServiceProvider(ServiceProvider):
    """ """

    def register(self) -> None:
        """ """

        self.app.singleton(EventBus)

        self.app.singleton(TaskManager)
        self.app.make(TaskManager)

        self.app.singleton(Console)
