from abc import ABC, abstractmethod
from typing import List, Type

from byte.container import Container
from byte.core.actors.base import Actor
from byte.core.actors.message import MessageBus


class ServiceProvider(ABC):
    """Base service provider class that all providers should extend.

    Implements the Service Provider pattern to organize dependency registration
    and initialization. Each provider encapsulates the setup logic for a specific
    domain or cross-cutting concern, promoting modular architecture.
    """

    def __init__(self):
        # Optional container reference for providers that need it during initialization
        self.container = None

    def provides_actors(self) -> List[Type[Actor]]:
        """Return list of actor classes this provider makes available."""
        return []

    async def boot_actors(self, container: Container):
        """Auto-register and boot all actors from provides_actors()"""
        actors = self.provides_actors()
        if not actors:
            return

        message_bus = await container.make(MessageBus)

        for actor_class in actors:
            # Create proper factory that provides all required arguments
            def make_actor(cls=actor_class, bus=message_bus, cont=container):
                # Use class name as actor name (lowercase)
                actor_name = cls.__name__.lower().replace("actor", "")
                return cls(actor_name, bus, cont)

            # Register with proper factory
            container.singleton(actor_class, make_actor)

            # Boot and setup subscriptions
            actor = await container.make(actor_class)
            await actor.setup_subscriptions(message_bus)

    def set_container(self, container: Container):
        """Set the container instance for providers that need container access.

        Allows providers to store a reference for complex initialization scenarios
        where the container is needed beyond the register/boot phases.
        """
        self.container = container

    @abstractmethod
    async def register(self, container: Container):
        """Register services in the container without initializing them.

        This is phase 1 of the two-phase initialization. Only bind service
        factories to the container - don't create instances or configure
        dependencies yet, as other providers may not be registered.
        """
        pass

    async def boot(self, container: Container):
        """Boot services after all providers have been registered.

        This is phase 2 where services can safely reference each other since
        all bindings are now available. Use this phase for:
        - Registering event listeners
        - Configuring service relationships
        - Performing initialization that requires other services
        """
        await self.boot_actors(container)

    async def shutdown(self, container: Container):
        """Shutdown services and clean up resources.

        Called during application shutdown to allow each provider to clean up
        its own resources. Override in providers that need cleanup.
        """
        pass

    def provides(self) -> list:
        """Return list of service identifiers this provider makes available.

        Used for documentation and potential dependency resolution validation.
        Should match the keys used in register() method calls.
        """
        return []
