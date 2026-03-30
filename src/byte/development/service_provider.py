from typing import List, Type

from byte.development import RecordResponseService
from byte.foundation import EventBus, Events
from byte.support import Service, ServiceProvider


class DevelopmentServiceProvider(ServiceProvider):
    """"""

    def services(self) -> List[Type[Service]]:
        return [RecordResponseService]

    async def boot(self):
        """Boot UI services."""
        event_bus = self.app.make(EventBus)

        event_bus.on(
            Events.PostBoot,
            self.boot_messages,
        )

    async def boot_messages(self, event: Events.PostBoot) -> Events.PostBoot:
        if self.app.is_development():
            event.messages.append("")
            event.messages.append("[$primary]Debug Info:[/$primary]")
            event.messages.append("Paths")
            event.messages.append(f"[$text-muted]Start:[/$text-muted] [$primary]{self.app['path']}[/$primary]")
            event.messages.append(f"[$text-muted]Root:[/$text-muted] [$primary]{self.app['path.root']}[/$primary]")
            event.messages.append(f"[$text-muted]Config:[/$text-muted] [$primary]{self.app['path.config']}[/$primary]")

        return event
