from abc import ABC
from typing import List, Type

from byte.container import Container
from byte.core.service.base_service import Service
from byte.domain.cli.service.command_registry import Command, CommandRegistry


class ServiceProvider(ABC):
    """Base service provider class that all providers should extend.

    Implements the Service Provider pattern to organize dependency registration
    and initialization. Each provider encapsulates the setup logic for a specific
    domain or cross-cutting concern, promoting modular architecture.
    """

    def __init__(self):
        # Optional container reference for providers that need it during initialization
        self.container = None

    def services(self) -> List[Type[Service]]:
        """Return list of service classes this provider makes available.

        Override this method to specify which service classes should be registered
        in the container when this provider is initialized. Services returned here
        will be automatically registered as singletons via register_services().
        """
        return []

    async def register_services(self, container: Container):
        """Register all services returned by services() as singletons in the container.

        Automatically registers each service class returned by the services() method
        as a singleton binding in the dependency injection container. Services will
        be instantiated with the container as their first argument when resolved.
        """
        services = self.services()
        if not services:
            return

        for service_class in services:
            container.singleton(service_class)

    def commands(self) -> List[Type[Command]]:
        """"""
        return []

    async def register_commands(self, container: Container):
        """"""
        commands = self.commands()
        if not commands:
            return

        for command_class in commands:
            container.bind(command_class)

    async def boot_commands(self, container: Container):
        """boot all commands from commands()"""
        commands = self.commands()
        if not commands:
            return

        command_registry = await container.make(CommandRegistry)

        for command_class in commands:
            command = await container.make(command_class)
            await command_registry.register_slash_command(command)

    def set_container(self, container: Container):
        """Set the container instance for providers that need container access.

        Allows providers to store a reference for complex initialization scenarios
        where the container is needed beyond the register/boot phases.
        """
        self.container = container

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
        pass

    async def shutdown(self, container: Container):
        """Shutdown services and clean up resources.

        Called during application shutdown to allow each provider to clean up
        its own resources. Override in providers that need cleanup.
        """
        pass
