from __future__ import annotations

from typing import TYPE_CHECKING

from byte import ServiceProvider

if TYPE_CHECKING:
    pass


class EventsServiceProvider(ServiceProvider):
    """ """

    # async def boot(self):
    #     event_bus = self.app.make(EventBus)
    #     # await event_bus.start()
