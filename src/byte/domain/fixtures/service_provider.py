from typing import List, Type

from byte.container import Container
from byte.core.event_bus import EventBus, EventType
from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.fixtures.service.fixture_recorder_service import FixtureRecorderService


class FixturesServiceProvider(ServiceProvider):
    """ """

    def services(self) -> List[Type[Service]]:
        return [FixtureRecorderService]

    async def boot(self, container: Container):
        """Boot file services and register commands with registry."""

        # Set up event listener for PRE_ASSISTANT_NODE
        event_bus = await container.make(EventBus)
        fixture_recorder_service = await container.make(FixtureRecorderService)

        event_bus.on(
            EventType.PRE_ASSISTANT_NODE.value,
            fixture_recorder_service.record_assistant_node_response,
        )
