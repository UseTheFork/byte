from typing import List, Type

from byte.container import Container
from byte.core import ByteConfig, EventBus, Service, TaskManager
from byte.domain.cli import CommandRegistry, ConsoleService


class TestContainerFactory:
    """Factory for creating test containers with minimal dependencies."""

    @staticmethod
    async def create_minimal(config: ByteConfig) -> Container:
        """Create a container with only core services registered.

        Usage: `container = await TestContainerFactory.create_minimal(test_config)`
        """
        container = Container()

        # Register core services that most tests need
        container.singleton(ByteConfig, lambda: config)
        container.singleton(EventBus)
        container.singleton(TaskManager)
        container.singleton(CommandRegistry)
        container.singleton(ConsoleService)

        return container

    @staticmethod
    async def create_with_services(config: ByteConfig, services: List[Type[Service]]) -> Container:
        """Create a container with core services plus specified domain services.

        Usage: `container = await TestContainerFactory.create_with_services(
            test_config,
            [FileService, GitService]
        )`
        """
        container = await TestContainerFactory.create_minimal(config)

        # Register additional services
        for service_class in services:
            container.singleton(service_class)

        # Boot all services
        for service_class in services:
            await container.make(service_class)

        return container
