from typing import List, Type

from byte.container import Container
from byte.core.event_bus import EventBus, EventType
from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.edit_format.service.edit_format_service import EditFormatService


class EditFormatProvider(ServiceProvider):
    """ """

    def services(self) -> List[Type[Service]]:
        return [EditFormatService]

    async def register(self, container: "Container"):
        """ """
        container.bind(EditFormatService)

    async def boot(self, container: Container):
        """Boot file services and register commands with registry."""
        # Ensure file discovery is booted first to scan project files
        edit_format_service = await container.make(EditFormatService)

        event_bus = await container.make(EventBus)
        event_bus.on(
            EventType.PRE_ASSISTANT_NODE.value,
            edit_format_service.replace_blocks_in_historic_messages_hook,
        )
