import asyncio
from typing import Any, Callable, Dict, Optional, Type, TypeVar

from byte.core.mixins.bootable import Bootable

T = TypeVar("T")


class Container:
    """Simple dependency injection container for managing service bindings.

    Implements the Service Locator pattern with support for both transient
    and singleton lifetimes. Services are resolved lazily on first access.
    """

    def __init__(self):
        self._singletons: Dict[Type, Callable[[], Any]] = {}
        self._transients: Dict[Type, Callable[[], Any]] = {}
        self._instances: Dict[Type, Any] = {}
        self._service_providers = []

    def bind(self, service_class: Type[T], concrete: Optional[Callable[[], T]] = None) -> None:
        """Register a transient service binding.

        Usage:
        container.bind(FileService, lambda: FileService(container))
        container.bind(FileService)  # Auto-creates with container
        """
        if concrete is None:

            def concrete():
                return service_class(self)

        self._transients[service_class] = concrete

    def singleton(self, service_class: Type[T], concrete: Optional[Callable[[], T]] = None) -> None:
        """Register a singleton service binding.

        Usage:
        container.singleton(FileService, lambda: FileService(container))
        container.singleton(FileService)  # Auto-creates with container
        """
        if concrete is None:
            # Auto-create factory for class
            def concrete():
                return service_class(self)

        self._singletons[service_class] = concrete

    async def _create_instance(self, factory: Callable, **kwargs) -> Any:
        """Helper to create and boot instances."""
        if asyncio.iscoroutinefunction(factory):
            instance = await factory()
        else:
            instance = factory()

        if isinstance(instance, Bootable):
            await instance.ensure_booted(**kwargs)

        return instance

    async def make(self, service_class: Type[T], **kwargs) -> T:
        """Resolve a service from the container.

        Usage:
        file_service = await container.make(FileService)
        """
        # Return cached singleton instance if available
        if service_class in self._instances:
            return self._instances[service_class]

        # Try to create from singleton bindings
        if service_class in self._singletons:
            factory = self._singletons[service_class]
            instance = await self._create_instance(factory, **kwargs)
            self._instances[service_class] = instance  # Cache it
            return instance

        # Try to create from transient bindings
        if service_class in self._transients:
            factory = self._transients[service_class]
            return await self._create_instance(factory, **kwargs)  # Don't cache

        raise ValueError(f"No binding found for {service_class.__name__}")

    def reset(self) -> None:
        """Reset the container state, clearing all bindings and instances.

        Usage: `container.reset()` -> clears all state for fresh start
        """
        self._singletons.clear()
        self._transients.clear()
        self._instances.clear()
        self._service_providers.clear()


# Global application container instance
# Using a global container simplifies service access across the application
# while maintaining the benefits of dependency injection
app = Container()
