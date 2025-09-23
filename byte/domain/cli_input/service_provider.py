from typing import List, Type

from byte.container import Container
from byte.core.actors.base import Actor
from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.cli_input.actor.input_actor import InputActor
from byte.domain.cli_input.actor.user_interaction_actor import UserInteractionActor
from byte.domain.cli_input.service.interactions_service import InteractionService


class CliInputServiceProvider(ServiceProvider):
    """Service provider for UI system."""

    def services(self) -> List[Type[Service]]:
        return [InteractionService]

    def actors(self) -> List[Type[Actor]]:
        return [InputActor, UserInteractionActor]

    async def register(self, container: Container) -> None:
        """Register UI services in the container."""

        # Register interaction service for user interactions
        container.singleton(InteractionService)

    async def boot(self, container: Container):
        """Boot UI services."""
        pass
