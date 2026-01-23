from byte.foundation import EventBus, EventType, Payload
from byte.support import ServiceProvider


class DevelopmentServiceProvider(ServiceProvider):
    """"""

    async def boot(self):
        """Boot UI services."""
        event_bus = self.app.make(EventBus)

        event_bus.on(
            EventType.POST_BOOT.value,
            self.boot_messages,
        )

    async def boot_messages(self, payload: Payload) -> Payload:
        if self.app.is_development():
            messages = payload.get("messages", [])

            messages.append("")
            messages.append("[primary]Debug Info:[/primary]")
            messages.append("Paths")
            messages.append(f"[muted]Start:[/muted] [primary]{self.app['path']}[/primary]")
            messages.append(f"[muted]Root:[/muted] [primary]{self.app['path.root']}[/primary]")
            messages.append(f"[muted]Config:[/muted] [primary]{self.app['path.config']}[/primary]")

            payload.set("messages", messages)

        return payload
