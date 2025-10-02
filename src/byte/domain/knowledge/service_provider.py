from typing import List, Type

from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.knowledge.service.conventions_service import ConventionsService


class KnowledgeServiceProvider(ServiceProvider):
    """Service provider for long-term knowledge management.

    Registers knowledge services for persistent storage of user preferences,
    project patterns, and learned behaviors. Enables cross-session memory
    and intelligent context building for the AI agent system.
    Usage: Register with container to enable long-term knowledge storage
    """

    def services(self) -> List[Type[Service]]:
        return [ConventionsService]

    # async def shutdown(self, container: "Container"):
    #     """Shutdown knowledge services and close database connections."""
    #     try:
    #         if KnowledgeService in container._instances:
    #             knowledge_service = await container.make(KnowledgeService)
    #             await knowledge_service.close()
    #     except Exception:
    #         pass  # Ignore cleanup errors during shutdown
