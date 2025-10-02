from typing import List, Type

from byte.container import Container
from byte.core.event_bus import EventBus, EventType
from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.knowledge.service.convention_context_service import (
    ConventionContextService,
)


class KnowledgeServiceProvider(ServiceProvider):
    """Service provider for long-term knowledge management.

    Registers knowledge services for persistent storage of user preferences,
    project patterns, and learned behaviors. Enables cross-session memory
    and intelligent context building for the AI agent system.
    Usage: Register with container to enable long-term knowledge storage
    """

    def services(self) -> List[Type[Service]]:
        return [ConventionContextService]

    async def boot(self, container: Container):
        """Boot file services and register commands with registry."""

        # Set up event listener for PRE_PROMPT_TOOLKIT
        event_bus = await container.make(EventBus)
        conventions_service = await container.make(ConventionContextService)

        # Register listener that calls list_in_context_files before each prompt
        event_bus.on(
            EventType.PRE_ASSISTANT_NODE.value,
            conventions_service.add_project_context,
        )

    # async def shutdown(self, container: "Container"):
    #     """Shutdown knowledge services and close database connections."""
    #     try:
    #         if KnowledgeService in container._instances:
    #             knowledge_service = await container.make(KnowledgeService)
    #             await knowledge_service.close()
    #     except Exception:
    #         pass  # Ignore cleanup errors during shutdown
